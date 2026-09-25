"""Tests for the German locale formatters used in generated documents."""

from decimal import Decimal

import pytest

from src.backend.formatting import format_price, format_quantity


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("0.00"), "0,00€"),
        (Decimal("55.00"), "55,00€"),
        (Decimal("82.50"), "82,50€"),
        (Decimal("123.75"), "123,75€"),
        (Decimal("1234.50"), "1.234,50€"),
        (Decimal("12345.67"), "12.345,67€"),
    ],
)
def test_format_price(value, expected):
    assert format_price(value) == expected


@pytest.mark.parametrize(
    ("net", "expected"),
    [
        (Decimal("440.00"), "83,60€"),
        (Decimal("1234.50"), "234,56€"),
        (Decimal("288.75"), "54,86€"),
        (Decimal("4210.00"), "799,90€"),
    ],
)
def test_format_price_rounds_vat_to_two_decimals(net, expected):
    """VAT of a net sum almost always carries more than two decimals."""
    assert format_price(net * Decimal("0.19")) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("0.00"), "0"),
        (Decimal("1.00"), "1"),
        (Decimal("2.00"), "2"),
        (Decimal("8.00"), "8"),
        (Decimal("0.50"), "0,5"),
        (Decimal("1.50"), "1,5"),
        (Decimal("7.50"), "7,5"),
    ],
)
def test_format_quantity(value, expected):
    assert format_quantity(value) == expected
