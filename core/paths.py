"""
Path and file discovery utilities for heinrich-tool.
"""
import logging
from pathlib import Path

from .config import Config

HEINRICH_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = HEINRICH_ROOT / "config.json"     # For import in cli.py

CSV_NAME_RE = "heinrich_zeiterfassung_*.csv"
TEMPLATES_DIR = HEINRICH_ROOT / "templates"
VORDRUCK_PATH = TEMPLATES_DIR / "Vordruck.docx"
INTERMEDIATE_ROOT = TEMPLATES_DIR / "intermediate"
INTERMEDIATE_FILENAME = "Vordruck_Rechnung_{project_number}.docx"


def _format_filename(template: str, **values: str) -> str:
    """Fill the filename template placeholders with values"""
    try:
        return template.format(**values)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Missing placeholder '{missing}' in filename template"
        ) from e


def get_project_dir(data_root: Path, project_number: str) -> Path:
    """Find the folder with the given 4-digit project number as prefix."""
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logging.info(f"Found project folder: {folder}")
            return folder
    raise FileNotFoundError(
        f"No folder found for project number {project_number}")


def get_latest_csv_path(project_dir: Path, config: Config) -> Path:
    """Find the latest CSV file in the order folder."""
    csv_files = sorted(project_dir.glob(config.filenames["CSV_NAME_RE"]))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {project_dir}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logging.info(f"Using CSV file: {latest}")
    return latest


def get_intermediate_project_dir(project_number: str) -> Path:
    """templates/intermediate/<project_number>/"""
    path = INTERMEDIATE_ROOT / project_number
    return path


def get_intermediate_rechnung_path(project_number: str) -> Path:
    """templates/intermediate/<project_number>/Vordruck_Rechnung_<project_number>.docx"""
    filename = _format_filename(
        INTERMEDIATE_FILENAME,
        project_number=project_number
    )
    path = get_intermediate_project_dir(project_number) / filename
    return path


def get_liefer_target_path(
        project_dir: Path,
        project_number: str,
        config: Config) -> Path:
    """Create filepath for Lieferschein using filename template from config"""
    template = config.filenames["LIEFERSCHEIN"]
    filename = _format_filename(
        template,
        project_number=project_number
    )
    path = project_dir / filename
    return path


def get_rechnung_target_path(
        project_dir: Path,
        project_number: str,
        receipt_number: str,
        config: Config) -> Path:
    """Create filepath for Rechnung using filename template from config"""
    template = config.filenames["RECHNUNG"]
    filename = _format_filename(
        template,
        project_number=project_number,
        receipt_number=receipt_number
    )
    path = project_dir / filename
    return path


def get_auftrag_target_path(
        project_dir: Path,
        project_number: str,
        receipt_number: str,
        config: Config) -> Path:
    """Create filepath for Auftragsbestätigung using filename template from config"""
    template = config.filenames["AUFTRAG"]
    filename = _format_filename(
        template,
        project_number=project_number,
        receipt_number=receipt_number
    )
    path = project_dir / filename
    return path
