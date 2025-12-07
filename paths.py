"""
Path and file discovery utilities for heinrich-tool.
"""
import logging
from pathlib import Path
from typing import Dict

HEINRICH_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = HEINRICH_ROOT / "config.json"

TEMPLATES_DIR = HEINRICH_ROOT / "templates"
VORDRUCK_PATH = TEMPLATES_DIR / "Vordruck.docx"
INTERMEDIATE_ROOT = TEMPLATES_DIR / "intermediate"


def get_project_dir(data_root: Path, project_number: str) -> Path:
    """Find the folder with the given 4-digit project number as prefix."""
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logging.info(f"Found project folder: {folder}")
            return folder
    raise FileNotFoundError(
        f"No folder found for project number {project_number}")


def get_latest_csv_path(project_dir: Path) -> Path:
    """Find the latest CSV file in the order folder."""
    csv_files = sorted(project_dir.glob('heinrich_zeiterfassung_*.csv'))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {project_dir}")
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


def get_liefer_target_path(project_dir: Path, project_number: str):
    liefer_path = project_dir / f"Lieferschein Nr. {project_number}.docx"
    return liefer_path


def get_rechnung_target_path(project_dir: Path, project_number: str, receipt_number: str):
    rechnung_path = project_dir / \
        f"Rechnung Nr. {project_number} - {receipt_number}.docx"
    return rechnung_path


def get_auftrag_target_path(project_dir: Path, project_number: str, receipt_number: str):
    auftrag_path = project_dir / \
        f"Auftragsbestaetigung Nr. {project_number} - {receipt_number}.docx"
    return auftrag_path
