import re


def strip_markup(text: str) -> str:
    """Strip the 5eTools-style inline markup from *text*.

    Handles patterns such as:

    - "{@variantrule Hit Points|XPHB}" -> "Hit Points"
    - "{@variantrule Emanation [Area of Effect]|XPHB|Emanation}" -> "Emanation"
    - "{@damage 1d6}" -> "1d6"

    If ``text`` is falsy ("" or ``None``), it is returned unchanged.
    """

    if not text:
        return text

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
    pattern_with_source = re.compile(
        r"\{@([^\s}]+)\s+([^|}\[]+)(?:\s*\[[^]]+])?\|[^}]*}"
    )

    def _repl_with_source(match: re.Match) -> str:
        return match.group(2).strip()

    cleaned = pattern_with_source.sub(_repl_with_source, text)

    # Then handle simpler commands with no "|source" part, such as
    # "{@damage 1d6}". In this case we keep everything after the command
    # name up to the closing brace.
    pattern_simple = re.compile(r"\{@([^\s}]+)\s+([^}]+)}")

    def _repl_simple(match: re.Match) -> str:
        return match.group(2).strip()

    return pattern_simple.sub(_repl_simple, cleaned)
