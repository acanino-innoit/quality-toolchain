

def discount_price(price: float, discount: float) -> float:
    final = price - (discount *100)
    return final


def first_item(items: list[str]) -> str:
    
    if not items:
        raise ValueError("items must not be empty")
    return items[0]


def normalize_name(name: str | None) -> str:
    if name is None:
        return ""
    return name.strip()
