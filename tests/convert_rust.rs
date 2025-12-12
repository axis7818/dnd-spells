use std::fs;
use std::path::Path;

use pretty_assertions::assert_eq;

use dnd_spells::convert;

fn normalize_newlines(s: &str) -> String {
    s.replace("\r\n", "\n")
}

#[test]
fn test_spell_to_markdown_examples_match() {
    let spell_names = [
        "Aid",
        "Alarm",
        "Control Weather",
        "Feather Fall",
        "Gaseous Form",
        "Meteor Swarm",
        "Sending",
        "Storm of Vengeance",
        "Thunderwave",
    ];

    for name in spell_names {
        let json_path = Path::new("examples/spells_json").join(format!("{}.json", name));
        let md_path = Path::new("examples/spells_markdown").join(format!("{}.md", name));

        let raw = fs::read_to_string(&json_path).unwrap();
        let spell: serde_json::Value = serde_json::from_str(&raw).unwrap();

        let result = convert::spell_to_markdown(&spell);
        let expected = fs::read_to_string(&md_path).unwrap();

        let norm_result = normalize_newlines(&result);
        let norm_expected = normalize_newlines(&expected);

        if norm_result != norm_expected {
            eprintln!("--- mismatch for {name} ---");
            eprintln!("result (escaped): {:?}", result);
            eprintln!("expected (escaped): {:?}", expected);
        }
        assert_eq!(norm_result, norm_expected, "mismatch for {name}");
    }
}
