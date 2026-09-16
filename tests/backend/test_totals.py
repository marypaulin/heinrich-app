"""Tests for net, VAT and gross calculation and their rendering as placeholders."""

import pytest

from src.backend.models import LineItem, Totals
from src.backend.placeholders import PH_SUM_GROSS, PH_SUM_NET, PH_VAT

VAT_RATE = 0.19


def hours_item(quantity: float, unit_price: float) -> LineItem:
    return LineItem(
        kind="hours",
        order_number="10012345",
        quantity=quantity,
        description="Meisterstunde zu Auftrag Nr. 10012345",
        unit_price=unit_price,
        total_price=quantity * unit_price,
    )


def material_item(unit_price: float) -> LineItem:
    return LineItem(
        kind="material",
        order_number="10012345",
        quantity=1.0,
        description="Material zu Auftrag Nr. 10012345",
        unit_price=unit_price,
        total_price=unit_price,
    )


def test_totals_of_a_single_hours_item():
    totals = Totals.calculate_sums_and_vat([hours_item(8.0, 55.0)], VAT_RATE)

    assert totals.sum_net == 440.00
    assert totals.vat == 83.60
    assert totals.sum_gross == 523.60


def test_totals_sum_hours_and_material():
    line_items = [
        hours_item(8.0, 55.0),
        hours_item(3.5, 82.5),
        material_item(212.35),
    ]

    totals = Totals.calculate_sums_and_vat(line_items, VAT_RATE)

    assert totals.sum_net == 941.10
    assert totals.vat == 178.81
    assert totals.sum_gross == 1119.91


def test_totals_of_no_line_items_are_zero():
    totals = Totals.calculate_sums_and_vat([], VAT_RATE)

    assert totals.sum_net == 0.0
    assert totals.vat == 0.0
    assert totals.sum_gross == 0.0


def test_vat_on_a_half_cent_is_rounded_up():
    totals = Totals.calculate_sums_and_vat([material_item(13.50)], VAT_RATE)

    assert totals.vat == 2.57


@pytest.mark.parametrize(
    "unit_price",
    [13.50, 0.50, 2.50, 4.50, 17.50, 288.75, 1234.50, 4210.00],
)
def test_printed_amounts_add_up(unit_price):
    """Net, VAT and gross are printed side by side; a customer can add them up."""
    totals = Totals.calculate_sums_and_vat([material_item(unit_price)], VAT_RATE)
    mapping = totals.to_mapping()

    def cents(amount: str) -> int:
        return int(amount.removesuffix("€").replace(".", "").replace(",", ""))

    assert cents(mapping[PH_SUM_NET]) + cents(mapping[PH_VAT]) == cents(
        mapping[PH_SUM_GROSS]
    )


def test_to_mapping_formats_every_placeholder():
    totals = Totals.calculate_sums_and_vat([hours_item(8.0, 55.0)], VAT_RATE)

    assert totals.to_mapping() == {
        PH_SUM_NET: "440,00€",
        PH_VAT: "83,60€",
        PH_SUM_GROSS: "523,60€",
    }
