import pytest
from src.get_entries import _fill_simplified


@pytest.mark.parametrize("traditional, simplified, expected", [("係呀", "系-", "系呀"), ("傍友", "--", "傍友"), ("頁數", "页数", "页数")])
def test_fill_simplfied(traditional, simplified, expected):
    assert _fill_simplified(traditional, simplified) == expected
