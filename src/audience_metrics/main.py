from audience_metrics import discount_price, first_item, normalize_name


def main() -> None:
    """Run the package with a small set of example inputs."""
    price = 100.0
    discount = 0.20
    items = ["news", "sports"]
    name = "  Ada  "

    print(f"Original price: {price:.2f}")
    print(f"Discount rate: {discount:.0%}")
    print(f"Discounted price: {discount_price(price, discount):.2f}")
    print(f"First item: {first_item(items)}")
    print(f"Normalized name: {normalize_name(name)}")
    print(f"Normalized name (None): {normalize_name(None)}")


if __name__ == "__main__":
    main()
