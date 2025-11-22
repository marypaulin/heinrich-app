"""
Path and file discovery utilities for heinrich-tool.
"""
import json
import logging
from pathlib import Path
from typing import Dict


def load_data_root_from_config(config_path: str = "config.json") -> Path:
    """Load DATA_ROOT from config.json."""
    with open(config_path, "r") as f:
        config = json.load(f)
    data_root = config["DATA_ROOT"]
    return Path(data_root)


DATA_ROOT = load_data_root_from_config()
TEMPLATE_DIR = Path('templates')
TEMPLATE_NAME = Path('Vordruck.docx')
OUTPUT_DIR = Path('output')


def find_project_folder(project_number: str) -> Path:
    """Find the order folder with the given 4-digit project number as prefix."""
    for folder in DATA_ROOT.iterdir():
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


def get_template_path() -> Path:
    """Get the path to the Word template."""
    path = TEMPLATE_DIR / TEMPLATE_NAME
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path


def create_output_dir(project_number: str):
    """Create the output directory if it doesn't exist."""
    project_output_dir = Path(OUTPUT_DIR / project_number)
    project_output_dir.mkdir(parents=True, exist_ok=True)


def get_rechnung_template_path(project_number: str) -> Path:
    """Get the path to the Rechnung Word template."""
    path = Path(OUTPUT_DIR / project_number /
                f"Vordruck_Rechnung_{project_number}.docx")
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


def clean_up_template(rechnung_template_path: Path):
    """Delete the Rechnung template file if it exists."""
    if rechnung_template_path.exists():
        rechnung_template_path.unlink()
        logging.info(f"Deleted temporary template: {rechnung_template_path}")
    else:
        logging.warning(
            f"Template to delete not found: {rechnung_template_path}")
