"""
CSV loading utility for heinrich-metallbau.
"""
import csv
from pathlib import Path
from typing import Dict, List


def load_csv_data(csv_path: str | Path) -> List[Dict[str, str]]:
    """Load CSV data as a list of dicts."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    # TODO: Transform/validate CSV data as needed for template
    return data
