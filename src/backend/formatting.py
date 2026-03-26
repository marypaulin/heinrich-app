def format_quantity(value: float) -> str:
    """Format a quantity value with one decimal,
    German locale (e.g. 1.5 -> 1,5; 2.0 -> 2)."""
    if value % 1 == 0:
        return str(int(value))
    return f"{round(value, 2):.1f}".replace(".", ",")


def format_price(value: float) -> str:
    """Format a price value with thousands separator and two decimals,
    German locale (e.g. 1234.5 -> 1.234,50 €)."""
    return (
        f"{round(value, 2):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        + "€"
    )
