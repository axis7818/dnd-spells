import json
from pathlib import Path

import pytest

from convert_spells import spell_to_markdown


@pytest.mark.parametrize(
    "spell_name",
    [
        "Aid",
        "Control Weather",
        "Gaseous Form",
        "Meteor Swarm",
        "Sending",
        "Storm of Vengeance",
    ],
)
def test_spell_to_markdown(spell_name):
    base_dir = Path(__file__).parent
    spell_json_dir = base_dir / "spells_json"
    spell_expected_dir = base_dir / "spells_expected"

    with (spell_json_dir / f"{spell_name}.json").open("r", encoding="utf-8") as f:
        spell = json.load(f)
    result = spell_to_markdown(spell)

    expected_markdown = (spell_expected_dir / f"{spell_name}.md").read_text(
        encoding="utf-8"
    )
    assert result == expected_markdown
