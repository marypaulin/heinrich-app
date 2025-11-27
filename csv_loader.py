"""
CSV loading utility for heinrich-metallbau.
"""
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

# Required fields that must be filled
REQUIRED_FIELDS = ["Auftrags-Nr.",
                   "Dauer (Std)", "Stundensatz (€)", "Material (€)"]


def load_hourly_rate_mapping_from_config(config_path: str = "config.json") -> Path:
    """Load HOURLY_RATE_MAPPING from config.json."""
    with open(config_path, "r") as f:
        config = json.load(f)
    hourly_rate_mapping = config["HOURLY_RATE_MAPPING"]
    return hourly_rate_mapping


HOURLY_RATE_MAPPING = load_hourly_rate_mapping_from_config()


def get_description(hourly_rate: float) -> str:
    """Get description based on hourly rate"""
    key = f"{hourly_rate:.2f}"
    if key in HOURLY_RATE_MAPPING:
        return HOURLY_RATE_MAPPING[key]
    logging.warning(
        f"Unknown hourly rate {hourly_rate}, using default description.")
    return HOURLY_RATE_MAPPING["DEFAULT"]


def parse_float(value: str) -> float:
    # Replace comma with dot, strip spaces, handle both "," and "."
    value = value.strip().replace(",", ".")
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid numeric value {value}")


def load_csv_data(csv_path: str | Path) -> List[Dict[str, str | int | float]]:
    """Load and transform CSV data to a list of dicts."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)

    # Check required fields
    for i, row in enumerate(rows, start=2):
        missing = [field for field in REQUIRED_FIELDS if not row.get(field)]
        if missing:
            raise ValueError(
                f"Missing value(s) in row {i}: {', '.join(missing)}")

    # Transform CSV rows according to the following rules:
    # - The result is a list of dicts with keys:
    #   "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # - For each row in CSV:
    # - If "Auftrags-Nr." is not eight digits, skip this row
    # - If "Material (€)" is 0, this row is a "Arbeitsstunden" row
    #   and the resulting dict will be:
    #   {
    #      "Menge": row["Dauer (Std)"],
    #      "Beschreibung": f"Meister/Helferstunde [Sonntag] zu Auftrag Nr. {row["Auftrags-Nr."]}",
    #      "€/Stk": row["Stundensatz (€)"],
    #      "Preis gesamt": row["Material (€)"] * row["Dauer (Std)"],
    #   }
    # - Otherwise, this row splits to two rows - one "Arbeitsstunden"
    #   and one "Material" row and the resulting dicts will be:
    #   1. Arbeitsstunden dict:
    #   {
    #      "Menge": row["Dauer (Std)"],
    #      "Beschreibung": f"Meister/Helferstunde [Sonntag] zu Auftrag Nr. {row["Auftrags-Nr."],
    #      "€/Stk": row["Stundensatz (€)"],
    #      "Preis gesamt": row["Stundensatz (€)"] * row["Dauer (Std)"],
    #   }
    #   2. Material dict:
    #   {
    #      "Menge": 1,
    #      "Beschreibung": row["Beschreibung"],
    #      "€/Stk": row["Material (€)"],
    #      "Preis gesamt": row["Material (€)"],
    #   }
    # - "Auftrags-Nr." should be converted to str
    # - "Dauer (Std)" should be converted to float
    # - Prices should be converted to float
    result = []
    for i, row in enumerate(rows, start=2):
        order_number = row["Auftrags-Nr."]
        if not order_number.isdigit() or len(order_number) != 8:
            logging.info(
                f"Skipping row {i} with invalid Auftrags-Nr.: {order_number}")
            continue
        try:
            duration = parse_float(row["Dauer (Std)"])
            hourly_rate = parse_float(row["Stundensatz (€)"])
            hourly_description = get_description(hourly_rate)
            material = parse_float(row["Material (€)"])
        except ValueError as e:
            raise ValueError(f"Error in row {i}: {e}") from e

        if material == 0:
            # Only Arbeitsstunden
            logging.info(
                f"Creating Arbeitsstunden row for Auftrags-Nr.: {order_number}")
            d = {
                "Menge": duration,
                "Beschreibung": f"{hourly_description} zu Auftrag Nr. {order_number}",
                "€/Stk": hourly_rate,
                "Preis gesamt": hourly_rate * duration,
            }
            result.append(d)
        else:
            # Both Arbeitsstunden and Material
            logging.info(
                f"Creating Arbeitsstunden row for Auftrags-Nr.: {order_number}")
            d = {
                "Menge": duration,
                "Beschreibung": f"{hourly_description} zu Auftrag Nr. {order_number}",
                "€/Stk": hourly_rate,
                "Preis gesamt": hourly_rate * duration,
            }
            logging.info(f"Result: {d}")
            result.append(d)
            logging.info(
                f"Creating Material row for Auftrags-Nr.: {order_number}")
            d = {
                "Menge": "1",
                "Beschreibung": f"Material zu Auftrag Nr. {order_number} ({row["Beschreibung"]})",
                "€/Stk": material,
                "Preis gesamt": material,
            }
            result.append(d)
    return result
