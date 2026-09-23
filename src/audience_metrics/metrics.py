def discount_price(price: float, discount: float) -> float:
    return price * (1 - discount)


def first_item(items: list[str]) -> str:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]


def normalize_name(name: str | None) -> str:
    if name is None:
        return ""
    return name.strip()
