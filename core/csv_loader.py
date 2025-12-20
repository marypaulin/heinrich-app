"""
CSV loading utility
"""
import csv
from datetime import date, datetime
from pathlib import Path
from typing import List

from .config import Config
from .models import CsvRow

CSV_COL_DATE = "Datum"
CSV_COL_ORDER_NUMBER = "Auftrags-Nr."
CSV_COL_DESC = "Beschreibung"
CSV_COL_DURATION = "Dauer (Std)"
CSV_COL_HOURLY_RATE = "Stundensatz (€)"
CSV_COL_MATERIAL = "Material (€)"
CSV_COL_TOTAL = "Gesamtkosten (€)"

# Required fields that must be filled
REQUIRED_FIELDS = [
    CSV_COL_ORDER_NUMBER,
    CSV_COL_DURATION,
    CSV_COL_HOURLY_RATE,
    CSV_COL_MATERIAL
]


def _parse_date(i: int, value: str, config: Config) -> date:
    """Parse str to date from config.date_format"""
    value = value.strip()
    try:
        return datetime.strptime(value, config.date_format)
    except ValueError:
        raise ValueError(f"Invalid date format in row {i}: {value}")


def _parse_float(i: int, value: str) -> float:
    """Replace comma with dot, strip spaces, handle both ',' and '.'"""
    value = value.strip().replace(",", ".")
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid numeric value in row {i}: {value}")


def load_csv_data(csv_path: Path, config: Config) -> List[CsvRow]:
    """
    Load and parse a CSV file into a list of CsvRow objects.

    This function is responsible for:
    - reading the CSV file,
    - validating required columns,
    - parsing strings into typed values (date, float),
    - and creating typed CsvRow domain objects.

    Column-to-attribute mapping:
        CSV column          → CsvRow attribute
        ---------------------------------------
        "Datum"             → date
        "Auftrags-Nr."      → order_number
        "Beschreibung"      → description
        "Dauer (Std)"       → duration_hours
        "Stundensatz (€)"   → hourly_rate
        "Material (€)"      → material_cost
        "Gesamtkosten (€)"  → total_cost

    Parameters:
        csv_path: Path to the CSV file to load.
        config: Application configuration (used for date parsing).

    Returns:
        A list of CsvRow objects representing the parsed CSV rows.

    Raises:
        ValueError: If required fields are missing or values cannot be parsed.
        FileNotFoundError: If the CSV file does not exist.
    """
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)

    result = []

    for i, row in enumerate(rows, start=2):
        # Check required fields
        missing = [field for field in REQUIRED_FIELDS if not row.get(field)]
        if missing:
            raise ValueError(
                f"Missing value(s) in row {i-1}: {', '.join(missing)}")

        csv_row = CsvRow(
            row_number=i-1,
            date=_parse_date(i-1, row[CSV_COL_DATE], config),
            order_number=row[CSV_COL_ORDER_NUMBER],
            description=row[CSV_COL_DESC],
            duration_hours=_parse_float(i-1, row[CSV_COL_DURATION]),
            hourly_rate=_parse_float(i-1, row[CSV_COL_HOURLY_RATE]),
            material_cost=_parse_float(i-1, row[CSV_COL_MATERIAL]),
            total_cost=_parse_float(i-1, row[CSV_COL_TOTAL])
        )
        result.append(csv_row)
    return result
