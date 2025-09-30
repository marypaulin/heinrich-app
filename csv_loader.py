"""
CSV loading utility for heinrich-metallbau.
"""
import csv
import logging
from pathlib import Path
from typing import Dict, List

# Required fields that must be filled
REQUIRED_FIELDS = ["Auftrags-Nr.", "Dauer (Std)", "Stundensatz (€)", "Material (€)"]


def load_csv_data(csv_path: str | Path) -> List[Dict[str, str]]:
    """Load and transform CSV data to a list of dicts."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)

    # Check required fields
    for i, row in enumerate(rows, start=2):
        missing = [field for field in REQUIRED_FIELDS if not row.get(field)]
        if missing:
            raise ValueError(f"Missing value(s) in row {i}: {', '.join(missing)}")

    # Transform CSV rows according to the following rules:
    # - The result is a list of dicts with keys:
    #   "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # - For each row in CSV:
    # - If "Auftrags-Nr." is not eight digits, skip this row
    # - If "Material (€)" is 0, this row is a "Arbeitsstunden" row
    #   and the resulting dict will be:
    #   {
    #      "Menge": row["Dauer (Std)"],
    #      "Beschreibung": f"Meisterstunde zu Auftrag Nr. {row["Auftrags-Nr."]}",
    #      "€/Stk": row["Stundensatz (€)"],
    #      "Preis gesamt": row["Material (€)"] * row["Dauer (Std)"],
    #   }
    # - Otherwise, this row splits to two rows - one "Arbeitsstunden"
    #   and one "Material" row and the resulting dicts will be:
    #   1. Arbeitsstunden dict:
    #   {
    #      "Menge": row["Dauer (Std)"],
    #      "Beschreibung": f"Meisterstunde zu Auftrag Nr. {row["Auftrags-Nr."],
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
    # - All numeric values (except for Auftragsnr.) should be converted to float
    #   and formatted to 2 decimal places
    result = []
    for i, row in enumerate(rows, start=2):
        auftrags_nr = row["Auftrags-Nr."]
        if not auftrags_nr.isdigit() or len(auftrags_nr) != 8:
            logging.info(f"Skipping row {i} with invalid Auftrags-Nr.: {auftrags_nr}")
            continue
        try:
            dauer = int(float((row["Dauer (Std)"])))
            stundensatz = float(row["Stundensatz (€)"])
            material = float(row["Material (€)"])
        except ValueError:
            raise ValueError(f"Invalid numeric value in row {i}")

        if material == 0:
            # Only Arbeitsstunden
            logging.info(f"Creating Arbeitsstunden row for Auftrags-Nr.: {auftrags_nr}")
            d = {
                "Menge": f"{dauer}",
                "Beschreibung": f"Meisterstunde zu Auftrag Nr. {auftrags_nr}",
                "€/Stk": f"{stundensatz:.2f}",
                "Preis gesamt": f"{(stundensatz * dauer):.2f}",
            }
            logging.info(f"Result: {d}")
            result.append(d)
        else:
            # Both Arbeitsstunden and Material
            logging.info(f"Creating Arbeitsstunden row for Auftrags-Nr.: {auftrags_nr}")
            d = {
                "Menge": f"{dauer}",
                "Beschreibung": f"Meisterstunde zu Auftrag Nr. {auftrags_nr}",
                "€/Stk": f"{stundensatz:.2f}",
                "Preis gesamt": f"{(stundensatz * dauer):.2f}",
            }
            logging.info(f"Result: {d}")
            result.append(d)
            logging.info(f"Creating Material row for Auftrags-Nr.: {auftrags_nr}")
            d = {
                "Menge": "1",
                "Beschreibung": row["Beschreibung"],
                "€/Stk": f"{material:.2f}",
                "Preis gesamt": f"{material:.2f}",
            }
            logging.info(f"Result: {d}")
            result.append(d)
    return result
