"""
Path and file discovery utilities for heinrich-metallbau.
"""
import logging
from pathlib import Path
from typing import Dict

DATA_ROOT = Path('RHI')
TEMPLATE_DIR = Path('templates')
TEMPLATE_NAME = 'Vordruck.docx'
OUTPUT_DIR = Path('output')




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


def get_output_paths(project_number: str, mode: str, order_number: str = None) -> Dict[str, Path]:
    """
    Return output paths for the given mode.
    For 'liefer': returns {'docx': ..., 'pdf': ...}
    For 'rechnung': returns scaffolded paths for 'auftragsbestaetigung' and 'rechnung' (docx/pdf)
    Raises ValueError if required arguments are missing.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    if mode == 'liefer':
        docx = OUTPUT_DIR / f"Lieferschein Nr. {project_number}.docx"
        pdf = OUTPUT_DIR / f"Lieferschein Nr. {project_number}.pdf"
        return {'docx': docx, 'pdf': pdf}
    elif mode == 'rechnung':
        if not order_number:
            raise ValueError("ORDER_NUMBER is required for 'rechnung' mode.")
        auftrag_docx = OUTPUT_DIR / f"Auftragsbestaetigung Nr. {project_number} - {order_number}.docx"
        auftrag_pdf = OUTPUT_DIR / f"Auftragsbestaetigung Nr. {project_number} - {order_number}.pdf"
        rechnung_docx = OUTPUT_DIR / f"Rechnung Nr. {project_number} - {order_number}.docx"
        rechnung_pdf = OUTPUT_DIR / f"Rechnung Nr. {project_number} - {order_number}.pdf"
        return {
            'auftragsbestaetigung_docx': auftrag_docx,
            'auftragsbestaetigung_pdf': auftrag_pdf,
            'rechnung_docx': rechnung_docx,
            'rechnung_pdf': rechnung_pdf
        }
    else:
        raise ValueError(f"Unknown mode: {mode}")
