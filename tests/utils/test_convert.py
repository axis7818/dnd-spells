import json
from pathlib import Path

import pytest

from utils.convert import spell_to_markdown


@pytest.mark.parametrize(
    "spell_name",
    [
        "Aid",
        "Alarm",
        "Control Weather",
        "Feather Fall",
        "Gaseous Form",
        "Meteor Swarm",
        "Sending",
        "Storm of Vengeance",
        "Thunderwave",
    ],
)
def test_spell_to_markdown(spell_name):
    spell_json_dir = Path("examples/spells_json")
    spell_expected_dir = Path("examples/spells_markdown")

    with (spell_json_dir / f"{spell_name}.json").open("r", encoding="utf-8") as f:
        spell = json.load(f)
    result = spell_to_markdown(spell)

    expected_markdown = (spell_expected_dir / f"{spell_name}.md").read_text(
        encoding="utf-8"
    )
    assert result == expected_markdown
