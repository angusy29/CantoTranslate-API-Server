import pytest
from src.get_entries import _fill_simplified, _split_numbered_definitions


@pytest.mark.parametrize("traditional, simplified, expected", [("係呀", "系-", "系呀"), ("傍友", "--", "傍友"), ("頁數", "页数", "页数")])
def test_fill_simplfied(traditional, simplified, expected):
    assert _fill_simplified(traditional, simplified) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1. first meaning 2. second meaning", ["first meaning", "second meaning"]),
        ("  no numbering here  ", ["no numbering here"]),
        ("1. only one", ["only one"]),
    ],
)
def test_split_numbered_definitions(text, expected):
    assert _split_numbered_definitions(text) == expected
