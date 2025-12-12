import pytest

from utils.markup import strip_markup


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("{@variantrule Hit Points|XPHB}", "Hit Points"),
        ("{@action Magic|XPHB}", "Magic"),
        ("{@variantrule Emanation [Area of Effect]|XPHB|Emanation}", "Emanation"),
        ("{@damage 1d6}", "1d6"),
        ("{@scaledamage 2d8|1-9|1d8}", "1d8"),
    ],
)
def test_strip_markup_variants(raw, expected):
    assert strip_markup(raw) == expected


def test_strip_markup_returns_original_for_none_or_empty():
    assert strip_markup("") == ""
    assert strip_markup(None) is None


def test_strip_markup_leaves_text_without_markup_unchanged():
    text = "This text has no special markup at all."
    assert strip_markup(text) == text
