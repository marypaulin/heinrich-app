"""Tests for reading the time-tracking CSV file into typed rows."""

from datetime import datetime
from pathlib import Path

import pytest

from src.backend.config import Config
from src.backend.csv_loader import load_csv_data
from src.backend.models import CsvRow

FIXTURE = Path(__file__).parents[1] / "fixtures" / "heinrich_zeiterfassung_sample.csv"
FIXTURE_DELIMITER = ";"

CONFIG = Config(
    data_root=Path("."),
    hourly_rate_mapping={},
    hourly_rate_default="",
    date_format="%d.%m.%Y",
    vat_rate=0.19,
    documents={},
    filenames={},
)


def write_variant(tmp_path: Path, row: int, column: str, value: str) -> Path:
    """Write the fixture with one field replaced; `row` counts data rows from 1."""
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(FIXTURE_DELIMITER)
    fields = lines[row].split(FIXTURE_DELIMITER)
    fields[header.index(column)] = f'"{value}"'
    lines[row] = FIXTURE_DELIMITER.join(fields)

    csv_path = tmp_path / "variant.csv"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path


# — Reading ———————————————————————————————————————————————————————————————————


def test_fixture_yields_all_rows_numbered_from_one():
    rows = load_csv_data(FIXTURE, CONFIG)

    assert [row.row_number for row in rows] == list(range(1, 9))


def test_first_row_is_read_completely():
    rows = load_csv_data(FIXTURE, CONFIG)

    assert rows[0] == CsvRow(
        row_number=1,
        date=datetime(2025, 7, 7),
        order_number="123",
        description="Zuschnitt Flachstahl",
        duration_hours=1.0,
        hourly_rate=65.0,
        material_cost=95.0,
        total_cost=160.0,
    )


def test_umlauts_and_sharp_s_survive():
    rows = load_csv_data(FIXTURE, CONFIG)

    assert rows[3].description == "Aufmaß Halle 3"
    assert rows[4].description == "Filtergehäuse prüfen"
    assert rows[6].description == "Geländer schweißen Ost"


def test_empty_description_stays_empty():
    rows = load_csv_data(FIXTURE, CONFIG)

    assert rows[7].description == ""


def test_file_with_bom_reads_like_file_without(tmp_path):
    csv_path = tmp_path / "with_bom.csv"
    csv_path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8-sig")

    assert load_csv_data(csv_path, CONFIG) == load_csv_data(FIXTURE, CONFIG)


def test_blank_order_number_becomes_empty(tmp_path):
    csv_path = write_variant(tmp_path, row=2, column="Auftrags-Nr.", value="   ")

    rows = load_csv_data(csv_path, CONFIG)

    assert rows[1].order_number == ""


# — Errors ————————————————————————————————————————————————————————————————————


@pytest.mark.parametrize("column", ["Dauer (Std)", "Stundensatz", "Material"])
def test_missing_required_value_is_rejected(tmp_path, column):
    csv_path = write_variant(tmp_path, row=1, column=column, value="")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, CONFIG)


def test_broken_number_is_rejected(tmp_path):
    csv_path = write_variant(tmp_path, row=1, column="Stundensatz", value="abc")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, CONFIG)


def test_broken_date_is_rejected(tmp_path):
    csv_path = write_variant(tmp_path, row=1, column="Datum", value="2025-07-07")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, CONFIG)


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv_data(tmp_path / "missing.csv", CONFIG)
