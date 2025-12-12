from __future__ import annotations

import re


_PATTERN_SCALEDAMAGE = re.compile(r"\{@scaledamage\s+[^|}]+\|[^|}]*\|([^}]+)}")
_PATTERN_WITH_SOURCE = re.compile(r"\{@([^\s}]+)\s+([^|}\[]+)(?:\s*\[[^]]+])?\|[^}]*}")
_PATTERN_SIMPLE = re.compile(r"\{@([^\s}]+)\s+([^}]+)}")


def strip_markup(text: str | None) -> str | None:
    """Strip the 5eTools-style inline markup from *text*.

    Handles patterns such as:

    - "{@variantrule Hit Points|XPHB}" -> "Hit Points"
    - "{@variantrule Emanation [Area of Effect]|XPHB|Emanation}" -> "Emanation"
    - "{@damage 1d6}" -> "1d6"
    - "{@scaledamage 2d8|1-9|1d8}" -> "1d8"

    If ``text`` is falsy ("" or ``None``), it is returned unchanged.
    """

    if not text:
        return text

    def _repl_scaledamage(match: re.Match) -> str:
        return match.group(1).strip()

    cleaned = _PATTERN_SCALEDAMAGE.sub(_repl_scaledamage, text)

    # First handle commands which include a trailing "|source" (and possibly
    # more pipe‑separated segments). We keep only the main display text before
    # any optional bracketed qualifier like " [Area of Effect]".
    #
    # Regex breakdown:
    #   \{@          - opening marker
    #   ([^\s}]+)    - command name (not used)
    #   \s+          - at least one space
    #   ([^|}\[]+)   - main display text up to '|' or ' ['
    #   (?:\s*\[[^]]+])? - optional " [kind]" section to be discarded
    #   \|          - separator before source/extra segments
    #   [^}]*        - the rest up to
    #   }            - closing brace
    def _repl_with_source(match: re.Match) -> str:
        return match.group(2).strip()

    cleaned = _PATTERN_WITH_SOURCE.sub(_repl_with_source, cleaned)

    # Then handle simpler commands with no "|source" part, such as
    # "{@damage 1d6}". In this case we keep everything after the command
    # name up to the closing brace.
    def _repl_simple(match: re.Match) -> str:
        return match.group(2).strip()

    return _PATTERN_SIMPLE.sub(_repl_simple, cleaned)
