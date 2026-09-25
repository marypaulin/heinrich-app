"""Tests for turning parsed CSV rows into document line items."""

from datetime import date
from pathlib import Path

from src.backend.config import Config
from src.backend.csv_transformer import csv_rows_to_line_items
from src.backend.models import CsvRow, LineItem

CONFIG = Config(
    data_root=Path("."),
    hourly_rate_mapping={85.0: "Meisterstunde", 48.0: "Helferstunde"},
    hourly_rate_default="Arbeitsstunde",
    date_format="%d.%m.%Y",
    vat_rate=0.19,
    documents={},
    filenames={},
)


def csv_row(
    order_number: str = "90010001",
    duration_hours: float = 3.0,
    hourly_rate: float = 85.0,
    material_cost: float = 0.0,
    row_number: int = 2,
) -> CsvRow:
    return CsvRow(
        row_number=row_number,
        date=date(2025, 7, 24),
        order_number=order_number,
        description="Rahmen Baugruppe 4",
        duration_hours=duration_hours,
        hourly_rate=hourly_rate,
        material_cost=material_cost,
        total_cost=duration_hours * hourly_rate + material_cost,
    )


# — Hours ———————————————————————————————————————————————————————————————————————


def test_row_without_material_becomes_one_hours_item():
    line_items, messages = csv_rows_to_line_items([csv_row()], CONFIG)

    assert line_items == [
        LineItem(
            kind="hours",
            order_number="90010001",
            quantity=3.0,
            description="Meisterstunde zu Auftrag Nr. 90010001",
            unit_price=85.0,
            total_price=255.0,
        )
    ]
    assert messages == []


def test_each_row_gets_the_description_of_its_hourly_rate():
    rows = [csv_row(hourly_rate=85.0), csv_row(hourly_rate=48.0)]

    line_items, _ = csv_rows_to_line_items(rows, CONFIG)

    assert [item.description for item in line_items] == [
        "Meisterstunde zu Auftrag Nr. 90010001",
        "Helferstunde zu Auftrag Nr. 90010001",
    ]


def test_unknown_hourly_rate_falls_back_to_default_with_warning():
    line_items, messages = csv_rows_to_line_items([csv_row(hourly_rate=82.5)], CONFIG)

    assert line_items[0].description == "Arbeitsstunde zu Auftrag Nr. 90010001"
    assert line_items[0].total_price == 247.5
    assert len(messages) == 1


# — Material ————————————————————————————————————————————————————————————————————


def test_material_adds_a_material_item_after_the_hours():
    line_items, messages = csv_rows_to_line_items(
        [csv_row(duration_hours=1.0, material_cost=95.0)], CONFIG
    )

    assert [item.kind for item in line_items] == ["hours", "material"]
    assert line_items[1] == LineItem(
        kind="material",
        order_number="90010001",
        quantity=1.0,
        description="Material zu Auftrag Nr. 90010001",
        unit_price=95.0,
        total_price=95.0,
    )
    assert messages == []


def test_row_without_hours_becomes_only_a_material_item():
    line_items, messages = csv_rows_to_line_items(
        [csv_row(duration_hours=0.0, material_cost=95.0)], CONFIG
    )

    assert line_items == [
        LineItem(
            kind="material",
            order_number="90010001",
            quantity=1.0,
            description="Material zu Auftrag Nr. 90010001",
            unit_price=95.0,
            total_price=95.0,
        )
    ]
    assert messages == []


# — Skipped rows ————————————————————————————————————————————————————————————————


def test_row_without_order_number_is_skipped_with_warning():
    rows = [
        csv_row(order_number="90010001", row_number=2),
        csv_row(order_number="", row_number=3),
        csv_row(order_number="90010002", row_number=4),
    ]

    line_items, messages = csv_rows_to_line_items(rows, CONFIG)

    assert [item.order_number for item in line_items] == ["90010001", "90010002"]
    assert len(messages) == 1


# — Order of items ——————————————————————————————————————————————————————————————


def test_items_follow_the_csv_order():
    rows = [
        csv_row(order_number="90010001", material_cost=30.0),
        csv_row(order_number="90010002"),
    ]

    line_items, _ = csv_rows_to_line_items(rows, CONFIG)

    assert [(item.order_number, item.kind) for item in line_items] == [
        ("90010001", "hours"),
        ("90010001", "material"),
        ("90010002", "hours"),
    ]
