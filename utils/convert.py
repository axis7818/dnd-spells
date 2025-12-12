from utils.markup import strip_markup

LEVEL_NAMES = {
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


def format_time(spell):
    t = (spell.get("time") or [{}])[0]
    number = t.get("number")
    unit = t.get("unit", "").lower()
    react_condition = t.get("condition")
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
    return f"{number}{code}" if number else code, react_condition


def format_range(spell):
    spell_range = spell.get("range") or {}
    spell_range_distance = spell_range.get("distance") or {}
    spell_range_type = spell_range.get("type")
    spell_range_distance_type = spell_range_distance.get("type")
    spell_range_distance_amount = spell_range_distance.get("amount")

    if spell_range_distance_type == "unlimited":
        return "Unlimited"
    if spell_range_distance_type == "self":
        return "Self"
    if spell_range_distance_type == "touch":
        return "Touch"
    if spell_range_distance_type and spell_range_distance_amount:
        return f"{spell_range_distance_amount} {spell_range_distance_type}"
    return spell_range_type or "Unknown"


def format_components(spell):
    comps = spell.get("components") or {}
    parts = []
    material_detail = None
    if comps.get("v"):
        parts.append("V")
    if comps.get("s"):
        parts.append("S")
    m = comps.get("m")
    if m:
        parts.append("M*")
        material_detail = strip_markup(str(m))
    return ", ".join(parts) or "None", material_detail


def format_duration(spell):
    d = (spell.get("duration") or [{}])[0]
    dtype = d.get("type")
    if dtype == "instant":
        return "Instant", False
    if dtype == "permanent":
        return "Permanent", False
    if dtype == "timed":
        dur = d.get("duration") or {}
        amount = dur.get("amount")
        unit = dur.get("type", "").lower()
        if unit == "round":
            unit_name = "Round" if amount == 1 else "Rounds"
        elif unit == "minute":
            unit_name = "Minute" if amount == 1 else "Minutes"
        elif unit == "hour":
            unit_name = "Hour" if amount == 1 else "Hours"
        else:
            unit_name = unit
        text = f"{amount} {unit_name}" if amount else unit_name
        conc = bool(d.get("concentration"))
        return text, conc
    return "Unknown", False


def is_ritual(spell):
    meta = spell.get("meta") or {}
    return bool(meta.get("ritual"))


def is_upcastable(spell):
    return bool(spell.get("entriesHigherLevel"))


def build_tags(spell, is_concentration: bool = False):
    tags = ["Spell"]
    level = spell.get("level", 0)
    tags.append(LEVEL_NAMES.get(level, f"Level{level}"))
    if is_concentration:
        tags.append("Concentration")
    if is_ritual(spell):
        tags.append("Ritual")
    if is_upcastable(spell):
        tags.append("Upcastable")
    return tags


def spell_to_markdown(spell) -> str:
    time_str, react_condition = format_time(spell)
    range_str = format_range(spell)
    comp_str, material_detail = format_components(spell)
    duration_str, conc = format_duration(spell)
    tags = build_tags(spell, conc)

    entries = spell.get("entries") or []
    entries_higher_level = spell.get("entriesHigherLevel") or []

    def flatten_entries(items):
        parts = []

        for it in items:
            # Plain text paragraph
            if isinstance(it, str):
                parts.append(it)
                continue

            if not isinstance(it, dict):
                continue

            it_type = it.get("type")

            # Nested entries block
            if it_type == "entries":
                inner = it.get("entries") or []
                parts.extend(flatten_entries(inner))

            # List of items (e.g., Alarm's audible/mental alarms)
            elif it_type == "list":
                items_list = it.get("items") or []
                for sub in items_list:
                    if isinstance(sub, dict) and sub.get("type") == "item":
                        name = sub.get("name")
                        sub_entries = sub.get("entries") or []
                        text = "\n".join(flatten_entries(sub_entries))
                        if name and text:
                            parts.append(f"## {name}\n\n{text}")
                        elif name:
                            parts.append(name)
                        elif text:
                            parts.append(text)
                    else:
                        # Fallback in case the structure is slightly different
                        parts.extend(flatten_entries([sub]))

            # Fallback: if an unexpected dict still has 'entries', recurse into it
            else:
                inner = it.get("entries") or []
                if inner:
                    parts.extend(flatten_entries(inner))

        return parts

    flat_entries = flatten_entries(entries)
    desc_text = "\n\n".join(strip_markup(e) for e in flat_entries)

    # Flatten higher-level slot text (e.g. "Using a Higher-Level Spell Slot")
    hl_lines: list[str] = []

    if entries_higher_level:
        for block in entries_higher_level:
            if not isinstance(block, dict):
                continue

            name = (block.get("name") or "").strip()
            block_entries = block.get("entries") or []
            flat_block_entries = flatten_entries(block_entries)
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
