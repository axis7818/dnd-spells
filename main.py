from __future__ import annotations

import argparse
import json
import re
import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from utils.convert import spell_to_markdown
from version import version

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT_DIR / "examples" / "all-spells.json"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output" / "spells"

_FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9_' -]+")


def _slugify_filename(name: str) -> str:
    safe = _FILENAME_SAFE_RE.sub("-", name).strip("-")
    return safe or "spell"


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a JSON array of D&D spells to Obsidian-friendly markdown."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to a JSON file containing a list/array of spells.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write markdown files into.",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Do not create the spells-<version>.zip archive.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    output_dir: Path = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    spells: list[dict[str, Any]] = json.loads(args.input.read_text(encoding="utf-8"))
    for spell in spells:
        name = str(spell.get("name") or "unnamed")
        out_path = output_dir / f"{_slugify_filename(name)}.md"
        out_path.write_text(spell_to_markdown(spell), encoding="utf-8")

    (output_dir / "_version.txt").write_text(version, encoding="utf-8")

    if not args.no_zip:
        shutil.make_archive(f"spells-{version}", "zip", str(output_dir))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
