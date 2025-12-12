use serde_json::Value;

use crate::markup::strip_markup_or_empty;

fn get_obj<'a>(v: &'a Value) -> Option<&'a serde_json::Map<String, Value>> {
    v.as_object()
}

fn get_array<'a>(v: &'a Value) -> Option<&'a Vec<Value>> {
    v.as_array()
}

fn get_str<'a>(v: &'a Value, key: &str) -> Option<&'a str> {
    v.get(key).and_then(|x| x.as_str())
}

fn get_bool(v: &Value, key: &str) -> bool {
    v.get(key).and_then(|x| x.as_bool()).unwrap_or(false)
}

const LEVEL_NAMES: &[(i64, &str)] = &[
    (0, "Cantrip"),
    (1, "1stLevel"),
    (2, "2ndLevel"),
    (3, "3rdLevel"),
    (4, "4thLevel"),
    (5, "5thLevel"),
    (6, "6thLevel"),
    (7, "7thLevel"),
    (8, "8thLevel"),
    (9, "9thLevel"),
];

fn level_name(level: i64) -> String {
    for (k, v) in LEVEL_NAMES {
        if *k == level {
            return (*v).to_string();
        }
    }
    format!("Level{}", level)
}

pub fn format_time(spell: &Value) -> (String, Option<String>) {
    let time_block = spell
        .get("time")
        .and_then(get_array)
        .and_then(|a| a.get(0))
        .unwrap_or(&Value::Null);

    let number = time_block.get("number").and_then(|v| v.as_i64());
    let unit = time_block
        .get("unit")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_lowercase();
    let react_condition = time_block
        .get("condition")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    let code = match unit.as_str() {
        "action" => "A".to_string(),
        "bonus action" => "BA".to_string(),
        "reaction" => "R".to_string(),
        "minute" => {
            if number == Some(1) {
                " Minute".to_string()
            } else {
                " Minutes".to_string()
            }
        }
        "hour" => {
            if number == Some(1) {
                " Hour".to_string()
            } else {
                " Hours".to_string()
            }
        }
        _ => {
            if unit.is_empty() {
                "?".to_string()
            } else {
                unit
            }
        }
    };

    let out = if let Some(n) = number {
        format!("{}{}", n, code)
    } else {
        code
    };

    (out, react_condition)
}

pub fn format_range(spell: &Value) -> String {
    let range_block = spell.get("range").unwrap_or(&Value::Null);
    let distance_block = range_block.get("distance").unwrap_or(&Value::Null);

    let range_type = get_str(range_block, "type");
    let distance_type = get_str(distance_block, "type");
    let distance_amount = distance_block.get("amount");

    match distance_type {
        Some("unlimited") => "Unlimited".to_string(),
        Some("self") => "Self".to_string(),
        Some("touch") => "Touch".to_string(),
        Some(dt) => {
            if let Some(amt) = distance_amount.and_then(|v| v.as_i64()) {
                format!("{} {}", amt, dt)
            } else {
                range_type.unwrap_or("Unknown").to_string()
            }
        }
        None => range_type.unwrap_or("Unknown").to_string(),
    }
}

pub fn format_components(spell: &Value) -> (String, Option<String>) {
    let comps = spell.get("components").unwrap_or(&Value::Null);

    let mut parts: Vec<&str> = Vec::new();
    let mut material_detail: Option<String> = None;

    if comps.get("v").and_then(|v| v.as_bool()).unwrap_or(false) {
        parts.push("V");
    }
    if comps.get("s").and_then(|v| v.as_bool()).unwrap_or(false) {
        parts.push("S");
    }

    let material = comps.get("m");
    if let Some(m) = material {
        if !m.is_null() {
            parts.push("M*");
            material_detail = if let Some(obj) = get_obj(m) {
                obj.get("text")
                    .and_then(|v| v.as_str())
                    .map(strip_markup_or_empty)
            } else if let Some(s) = m.as_str() {
                Some(strip_markup_or_empty(s))
            } else {
                Some(strip_markup_or_empty(&m.to_string()))
            };
        }
    }

    let comp_str = if parts.is_empty() {
        "None".to_string()
    } else {
        parts.join(", ")
    };

    (comp_str, material_detail)
}

pub fn format_duration(spell: &Value) -> (String, bool) {
    let duration_block = spell
        .get("duration")
        .and_then(get_array)
        .and_then(|a| a.get(0))
        .unwrap_or(&Value::Null);

    let dtype = get_str(duration_block, "type").unwrap_or("");
    match dtype {
        "instant" => ("Instant".to_string(), false),
        "permanent" => ("Permanent".to_string(), false),
        "timed" => {
            let dur = duration_block.get("duration").unwrap_or(&Value::Null);
            let amount = dur.get("amount").and_then(|v| v.as_i64());
            let unit = dur
                .get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_lowercase();

            let unit_name = match unit.as_str() {
                "round" => {
                    if amount == Some(1) {
                        "Round".to_string()
                    } else {
                        "Rounds".to_string()
                    }
                }
                "minute" => {
                    if amount == Some(1) {
                        "Minute".to_string()
                    } else {
                        "Minutes".to_string()
                    }
                }
                "hour" => {
                    if amount == Some(1) {
                        "Hour".to_string()
                    } else {
                        "Hours".to_string()
                    }
                }
                _ => unit,
            };

            let text = if let Some(a) = amount {
                format!("{} {}", a, unit_name)
            } else {
                unit_name
            };

            let conc = duration_block
                .get("concentration")
                .and_then(|v| v.as_bool())
                .unwrap_or(false);
            (text, conc)
        }
        _ => ("Unknown".to_string(), false),
    }
}

pub fn is_ritual(spell: &Value) -> bool {
    let meta = spell.get("meta").unwrap_or(&Value::Null);
    get_bool(meta, "ritual")
}

pub fn is_upcastable(spell: &Value) -> bool {
    spell
        .get("entriesHigherLevel")
        .and_then(|v| v.as_array())
        .map(|a| !a.is_empty())
        .unwrap_or(false)
}

pub fn build_tags(spell: &Value, is_concentration: bool) -> Vec<String> {
    let mut tags: Vec<String> = vec!["Spell".to_string()];
    let level = spell.get("level").and_then(|v| v.as_i64()).unwrap_or(0);
    tags.push(level_name(level));

    if is_concentration {
        tags.push("Concentration".to_string());
    }
    if is_ritual(spell) {
        tags.push("Ritual".to_string());
    }
    if is_upcastable(spell) {
        tags.push("Upcastable".to_string());
    }

    tags
}

fn flatten_entries(items: &[Value]) -> Vec<String> {
    let mut parts: Vec<String> = Vec::new();

    for item in items {
        if let Some(s) = item.as_str() {
            parts.push(s.to_string());
            continue;
        }

        let Some(map) = item.as_object() else { continue };
        let item_type = map.get("type").and_then(|v| v.as_str()).unwrap_or("");

        if item_type == "entries" {
            let inner = map.get("entries").and_then(|v| v.as_array()).cloned().unwrap_or_default();
            parts.extend(flatten_entries(&inner));
        } else if item_type == "list" {
            let items_list = map.get("items").and_then(|v| v.as_array()).cloned().unwrap_or_default();
            for sub in items_list {
                if let Some(sub_map) = sub.as_object() {
                    if sub_map.get("type").and_then(|v| v.as_str()) == Some("item") {
                        let name = sub_map.get("name").and_then(|v| v.as_str());
                        let sub_entries = sub_map
                            .get("entries")
                            .and_then(|v| v.as_array())
                            .cloned()
                            .unwrap_or_default();
                        let text = flatten_entries(&sub_entries).join("\n");

                        match (name, text.trim().is_empty()) {
                            (Some(n), false) => parts.push(format!("## {}\n\n{}", n, text)),
                            (Some(n), true) => parts.push(n.to_string()),
                            (None, false) => parts.push(text),
                            (None, true) => {}
                        }
                        continue;
                    }
                }
                parts.extend(flatten_entries(&[sub]));
            }
        } else {
            let inner = map.get("entries").and_then(|v| v.as_array()).cloned().unwrap_or_default();
            if !inner.is_empty() {
                parts.extend(flatten_entries(&inner));
            }
        }
    }

    parts
}

pub fn spell_to_markdown(spell: &Value) -> String {
    let (time_str, react_condition) = format_time(spell);
    let range_str = format_range(spell);
    let (comp_str, material_detail) = format_components(spell);
    let (duration_str, conc) = format_duration(spell);
    let tags = build_tags(spell, conc);

    let entries = spell.get("entries").and_then(|v| v.as_array()).cloned().unwrap_or_default();
    let entries_higher_level = spell
        .get("entriesHigherLevel")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    let flat_entries = flatten_entries(&entries);
    let desc_text = flat_entries
        .into_iter()
        .map(|e| strip_markup_or_empty(&e))
        .collect::<Vec<_>>()
        .join("\n\n");

    let mut hl_lines: Vec<String> = Vec::new();
    if !entries_higher_level.is_empty() {
        for block in entries_higher_level {
            let Some(block_map) = block.as_object() else { continue };
            let mut name = block_map
                .get("name")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .trim()
                .to_string();

            let block_entries = block_map
                .get("entries")
                .and_then(|v| v.as_array())
                .cloned()
                .unwrap_or_default();

            let flat_block_entries = flatten_entries(&block_entries);
            let text = flat_block_entries
                .into_iter()
                .map(|p| strip_markup_or_empty(&p).trim().to_string())
                .filter(|p| !p.is_empty())
                .collect::<Vec<_>>()
                .join(" ")
                .trim()
                .to_string();

            if text.is_empty() {
                continue;
            }

            if !name.is_empty() {
                if !name.ends_with('.') {
                    name.push('.');
                }
                hl_lines.push(format!("**_{}_** {}", name, text));
            } else {
                hl_lines.push(text);
            }
        }
    }

    let mut lines: Vec<String> = Vec::new();
    lines.push("---".to_string());
    lines.push("tags:".to_string());
    for t in tags {
        lines.push(format!("  - {}", t));
    }
    lines.push(format!("Time: {}", time_str));
    lines.push(format!("range: {}", range_str));
    lines.push(format!("Components: {}", comp_str));
    lines.push(format!("Duration: {}", duration_str));
    lines.push("---".to_string());

    if let Some(cond) = react_condition {
        lines.push(format!("A reaction {}", cond));
        lines.push(String::new());
    }

    lines.push(desc_text.trim().to_string());

    if !hl_lines.is_empty() {
        lines.push(String::new());
        lines.extend(hl_lines);
    }

    if let Some(md) = material_detail {
        lines.push(String::new());
        lines.push(format!("\\* {}", md));
    }

    let out = lines.join("\n");
    format!("{}\n", out.trim())
}
