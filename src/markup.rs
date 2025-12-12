use regex::Regex;

pub fn strip_markup(text: Option<&str>) -> Option<String> {
    let Some(text) = text else { return None };
    if text.is_empty() {
        return Some(text.to_string());
    }

    // {@scaledamage 2d8|1-9|1d8} -> 1d8
    let pattern_scaledamage =
        Regex::new(r"\{@scaledamage\s+[^|}]+\|[^|}]*\|([^}]+)}").expect("valid regex");

    // {@variantrule Hit Points|XPHB} -> Hit Points
    // {@variantrule Emanation [Area of Effect]|XPHB|Emanation} -> Emanation
    let pattern_with_source =
        Regex::new(r"\{@([^\s}]+)\s+([^|}\[]+)(?:\s*\[[^]]+])?\|[^}]*}").expect("valid regex");

    // {@damage 1d6} -> 1d6
    let pattern_simple = Regex::new(r"\{@([^\s}]+)\s+([^}]+)}").expect("valid regex");

    let cleaned = pattern_scaledamage
        .replace_all(text, |caps: &regex::Captures<'_>| {
            caps[1].trim().to_string()
        })
        .to_string();

    let cleaned = pattern_with_source
        .replace_all(&cleaned, |caps: &regex::Captures<'_>| {
            caps[2].trim().to_string()
        })
        .to_string();

    let cleaned = pattern_simple
        .replace_all(&cleaned, |caps: &regex::Captures<'_>| {
            caps[2].trim().to_string()
        })
        .to_string();

    Some(cleaned)
}

pub fn strip_markup_or_empty(text: &str) -> String {
    strip_markup(Some(text)).unwrap_or_default()
}
