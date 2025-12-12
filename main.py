import shutil
import json
import re
from pathlib import Path

from version import version
from utils.convert import spell_to_markdown

ROOT = Path(__file__).parent
INPUT = ROOT / "examples/all-spells.json"
OUTPUT_DIR = ROOT / "output/spells"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    with INPUT.open("r", encoding="utf-8") as f:
        spells = json.load(f)

    for spell in spells:
        name = spell.get("name", "unnamed")
        safe_name = re.sub(r"[^A-Za-z0-9_' -]+", "-", name).strip("-") or "spell"
        md = spell_to_markdown(spell)
        out_path = OUTPUT_DIR / f"{safe_name}.md"
        with out_path.open("w", encoding="utf-8") as outf:
            outf.write(md)

        out_version_path = OUTPUT_DIR / "_version.txt"
        with out_version_path.open("w", encoding="utf-8") as outf:
            outf.write(version)

    shutil.make_archive(f"spells-{version}", "zip", OUTPUT_DIR)


if __name__ == "__main__":
    main()
