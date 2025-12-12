use pretty_assertions::assert_eq;

use dnd_spells::markup;

#[test]
fn test_strip_markup_variants() {
    let cases = [
        ("{@variantrule Hit Points|XPHB}", "Hit Points"),
        ("{@action Magic|XPHB}", "Magic"),
        (
            "{@variantrule Emanation [Area of Effect]|XPHB|Emanation}",
            "Emanation",
        ),
        ("{@damage 1d6}", "1d6"),
        ("{@scaledamage 2d8|1-9|1d8}", "1d8"),
    ];

    for (raw, expected) in cases {
        assert_eq!(markup::strip_markup(Some(raw)).unwrap(), expected);
    }
}

#[test]
fn test_strip_markup_returns_original_for_empty() {
    assert_eq!(markup::strip_markup(Some("")).unwrap(), "");
}

#[test]
fn test_strip_markup_leaves_text_without_markup_unchanged() {
    let text = "This text has no special markup at all.";
    assert_eq!(markup::strip_markup(Some(text)).unwrap(), text);
}
