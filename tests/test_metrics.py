import pytest

from audience_metrics import discount_price, first_item, normalize_name


def test_discount_price_applies_a_rate() -> None:
    assert discount_price(100.0, 0.20) == pytest.approx(80.0)


def test_first_item_returns_the_first_value() -> None:
    assert first_item(["news", "sports"]) == "news"


def test_first_item_rejects_an_empty_list() -> None:
    with pytest.raises(ValueError, match="items must not be empty"):
        first_item([])


def test_normalize_name_strips_text() -> None:
    assert normalize_name("  Ada  ") == "Ada"


def test_normalize_name_accepts_none() -> None:
    assert normalize_name(None) == ""
