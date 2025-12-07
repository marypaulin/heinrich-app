"""
Path and file discovery utilities for heinrich-tool.
"""
import logging
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.json"

TEMPLATES_DIR = PROJECT_ROOT / "templates"
VORDRUCK_PATH = TEMPLATES_DIR / "Vordruck.docx"
INTERMEDIATE_ROOT = TEMPLATES_DIR / "intermediate"


def find_project_folder(data_root: Path, project_number: str) -> Path:
    """Find the order folder with the given 4-digit project number as prefix."""
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logging.info(f"Found order folder: {folder}")
            return folder
    raise FileNotFoundError(
        f"No folder found for project number {project_number}")


def find_latest_csv(order_folder: Path) -> Path:
    """Find the latest CSV file in the order folder."""
    csv_files = sorted(order_folder.glob('heinrich_zeiterfassung_*.csv'))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {order_folder}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logging.info(f"Using CSV file: {latest}")
    return latest


def get_intermediate_project_dir(project_number: str) -> Path:
    """templates/intermediate/<project_number>/"""
    return INTERMEDIATE_ROOT / project_number


def get_intermediate_rechnung_path(project_number: str) -> Path:
    """templates/intermediate/<project_number>/Vordruck_Rechnung_<project_number>.docx"""
    path = get_intermediate_project_dir(
        project_number) / f"Vordruck_Rechnung_{project_number}.docx"
    return path


def get_target_paths(
        project_folder: Path,
        project_number: str,
        mode: str,
        order_number: str | None = None) -> Dict[str, Path]:
    """
    Return docx output paths for the given mode.
    For 'liefer': returns {'liefer': liefer_path}
    For 'rechnung': returns {'auftrag': auftrag_path, 'rechnung': rechnung_path}
    """

    if mode == 'liefer':
        liefer_path = Path(project_folder /
                           f"Lieferschein Nr. {project_number}.docx")
        return {'liefer': liefer_path}
    elif mode == 'rechnung':
        if not order_number:
            raise ValueError("ORDER_NUMBER is required for 'rechnung' mode.")
        auftrag_path = Path(project_folder /
                            f"Auftragsbestaetigung Nr. {project_number} - {order_number}.docx")
        rechnung_path = Path(project_folder /
                             f"Rechnung Nr. {project_number} - {order_number}.docx")
        return {
            'auftrag': auftrag_path,
            'rechnung': rechnung_path,
        }
    else:
        # Defensive programming: validate inputs at function boundary
        raise ValueError(f"Unknown mode: {mode}")
