"""Tests for the German locale formatters used in generated documents."""

import pytest

from src.backend.formatting import format_price, format_quantity


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, "0,00€"),
        (55.0, "55,00€"),
        (82.5, "82,50€"),
        (123.75, "123,75€"),
        (1234.5, "1.234,50€"),
        (12345.67, "12.345,67€"),
    ],
)
def test_format_price(value, expected):
    assert format_price(value) == expected


@pytest.mark.parametrize(
    ("net", "expected"),
    [
        (440.0, "83,60€"),
        (1234.5, "234,56€"),
        (288.75, "54,86€"),
        (4210.0, "799,90€"),
    ],
)
def test_format_price_rounds_vat_to_two_decimals(net, expected):
    """VAT of a net sum almost always carries more than two decimals."""
    assert format_price(net * 0.19) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, "0"),
        (1.0, "1"),
        (2.0, "2"),
        (8.0, "8"),
        (0.5, "0,5"),
        (1.5, "1,5"),
        (7.5, "7,5"),
    ],
)
def test_format_quantity(value, expected):
    assert format_quantity(value) == expected
