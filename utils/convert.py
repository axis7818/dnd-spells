from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from utils.markup import strip_markup

Spell = Mapping[str, Any]


LEVEL_NAMES: dict[int, str] = {
    0: "Cantrip",
    1: "1stLevel",
    2: "2ndLevel",
    3: "3rdLevel",
    4: "4thLevel",
    5: "5thLevel",
    6: "6thLevel",
    7: "7thLevel",
    8: "8thLevel",
    9: "9thLevel",
}


def format_time(spell: Spell) -> tuple[str, str | None]:
    time_block = (spell.get("time") or [{}])[0]
    number = time_block.get("number")
    unit = str(time_block.get("unit") or "").lower()
    react_condition = time_block.get("condition")
    if unit == "action":
        code = "A"
    elif unit == "bonus action":
        code = "BA"
    elif unit == "reaction":
        code = "R"
    elif unit == "minute":
        code = " Minute" if number == 1 else " Minutes"
    elif unit == "hour":
        code = " Hour" if number == 1 else " Hours"
    else:
        code = unit or "?"

    return (f"{number}{code}" if number else code), react_condition


def format_range(spell: Spell) -> str:
    range_block = spell.get("range") or {}
    distance_block = range_block.get("distance") or {}
    range_type = range_block.get("type")
    distance_type = distance_block.get("type")
    distance_amount = distance_block.get("amount")

    if distance_type == "unlimited":
        return "Unlimited"
    if distance_type == "self":
        return "Self"
    if distance_type == "touch":
        return "Touch"
    if distance_type and distance_amount is not None:
        return f"{distance_amount} {distance_type}"
    return range_type or "Unknown"


def format_components(spell: Spell) -> tuple[str, str | None]:
    comps = spell.get("components") or {}
    parts: list[str] = []
    material_detail: str | None = None
    if comps.get("v"):
        parts.append("V")
    if comps.get("s"):
        parts.append("S")
    material = comps.get("m")
    if material:
        parts.append("M*")
        try:
            material_detail = strip_markup(material["text"])
        except (KeyError, TypeError):
            material_detail = strip_markup(str(material))
    return ", ".join(parts) or "None", material_detail


def format_duration(spell: Spell) -> tuple[str, bool]:
    duration_block = (spell.get("duration") or [{}])[0]
    dtype = duration_block.get("type")
    if dtype == "instant":
        return "Instant", False
    if dtype == "permanent":
        return "Permanent", False
    if dtype == "timed":
        dur = duration_block.get("duration") or {}
        amount = dur.get("amount")
        unit = str(dur.get("type") or "").lower()
        if unit == "round":
            unit_name = "Round" if amount == 1 else "Rounds"
        elif unit == "minute":
            unit_name = "Minute" if amount == 1 else "Minutes"
        elif unit == "hour":
            unit_name = "Hour" if amount == 1 else "Hours"
        else:
            unit_name = unit
        text = f"{amount} {unit_name}" if amount else unit_name
        conc = bool(duration_block.get("concentration"))
        return text, conc
    return "Unknown", False


def is_ritual(spell: Spell) -> bool:
    meta = spell.get("meta") or {}
    return bool(meta.get("ritual"))


def is_upcastable(spell: Spell) -> bool:
    return bool(spell.get("entriesHigherLevel"))


def build_tags(spell: Spell, is_concentration: bool = False) -> list[str]:
    tags: list[str] = ["Spell"]
    level = spell.get("level", 0)
    tags.append(LEVEL_NAMES.get(level, f"Level{level}"))
    if is_concentration:
        tags.append("Concentration")
    if is_ritual(spell):
        tags.append("Ritual")
    if is_upcastable(spell):
        tags.append("Upcastable")
    return tags


def _flatten_entries(items: Sequence[Any]) -> list[str]:
    parts: list[str] = []

    for item in items:
        # Plain text paragraph
        if isinstance(item, str):
            parts.append(item)
            continue

        if not isinstance(item, Mapping):
            continue

        item_type = item.get("type")

        # Nested entries block
        if item_type == "entries":
            inner = item.get("entries") or []
            parts.extend(_flatten_entries(inner))

        # List of items (e.g., Alarm's audible/mental alarms)
        elif item_type == "list":
            items_list = item.get("items") or []
            for sub in items_list:
                if isinstance(sub, Mapping) and sub.get("type") == "item":
                    name = sub.get("name")
                    sub_entries = sub.get("entries") or []
                    text = "\n".join(_flatten_entries(sub_entries))
                    if name and text:
                        parts.append(f"## {name}\n\n{text}")
                    elif name:
                        parts.append(str(name))
                    elif text:
                        parts.append(text)
                else:
                    # Fallback in case the structure is slightly different
                    parts.extend(_flatten_entries([sub]))

        # Fallback: if an unexpected dict still has 'entries', recurse into it
        else:
            inner = item.get("entries") or []
            if inner:
                parts.extend(_flatten_entries(inner))

    return parts


def spell_to_markdown(spell: Spell) -> str:
    time_str, react_condition = format_time(spell)
    range_str = format_range(spell)
    comp_str, material_detail = format_components(spell)
    duration_str, conc = format_duration(spell)
    tags = build_tags(spell, conc)

    entries = spell.get("entries") or []
    entries_higher_level = spell.get("entriesHigherLevel") or []

    flat_entries = _flatten_entries(entries)
    desc_text = "\n\n".join(strip_markup(e) for e in flat_entries)

    # Flatten higher-level slot text (e.g. "Using a Higher-Level Spell Slot")
    hl_lines: list[str] = []

    if entries_higher_level:
        for block in entries_higher_level:
            if not isinstance(block, dict):
                continue

            name = (block.get("name") or "").strip()
            block_entries = block.get("entries") or []
            flat_block_entries = _flatten_entries(block_entries)
            text = " ".join(
                strip_markup(part).strip()
                for part in flat_block_entries
                if isinstance(part, str) and part.strip()
            ).strip()

            if not text:
                continue

            if name:
                # Ensure a trailing period on the heading, matching expected output.
                if not name.endswith("."):
                    name = f"{name}."
                hl_lines.append(f"**_{name}_** {text}")
            else:
                hl_lines.append(text)

    lines = ["---", "tags:"]
    for t in tags:
        lines.append(f"  - {t}")
    lines.extend(
        [
            f"Time: {time_str}",
            f"range: {range_str}",
            f"Components: {comp_str}",
            f"Duration: {duration_str}",
            "---",
        ]
    )

    if react_condition:
        lines.append(f"A reaction {react_condition}")
        lines.append("")

    lines.append(desc_text.strip())

    if hl_lines:
        lines.append("")
        lines.extend(hl_lines)

    if material_detail:
        lines.append("")
        lines.append(f"\\* {material_detail}")

    return "\n".join(lines).strip() + "\n"
