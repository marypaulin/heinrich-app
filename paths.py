"""
Path and file discovery utilities for heinrich-metallbau.
"""
import logging
from pathlib import Path
from typing import Optional

DATA_ROOT = Path('RHI')
TEMPLATE_DIR = Path('templates')
TEMPLATE_NAME = 'Vordruck.docx'


def find_order_folder(project_number: str) -> Path:
    """Find the order folder with the given 4-digit project number as prefix."""
    for folder in DATA_ROOT.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logging.info(f"Found order folder: {folder}")
            return folder
    raise FileNotFoundError(f"No folder found for project number {project_number}")


def find_latest_csv(order_folder: Path) -> Path:
    """Find the latest CSV file in the order folder."""
    csv_files = sorted(order_folder.glob('heinrich_zeiterfassung_*.csv'))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {order_folder}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logging.info(f"Using CSV file: {latest}")
    return latest


def get_template_path() -> Path:
    """Get the path to the Word template."""
    path = TEMPLATE_DIR / TEMPLATE_NAME
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path
