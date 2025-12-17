from pathlib import Path
from typing import List

from core.config import Config
from docgen import render_lieferschein_docx, render_rechnung_and_auftrag_docx
from models import LineItem
from paths import (get_auftrag_target_path, get_liefer_target_path,
                   get_rechnung_target_path)
from pdfgen import render_pdf


def render_lieferschein(
        project_number: str,
        line_items: List[LineItem],
        project_dir: Path,
        config: Config) -> None:
    """Render Lieferschein in DOCX and PDF format"""
    target_path = get_liefer_target_path(project_dir, project_number)
    render_lieferschein_docx(project_number, line_items, target_path, config)
    render_pdf(target_path)


def render_rechnung_and_auftrag(
        project_number: str,
        receipt_number: str,
        project_dir: Path) -> None:
    """Render Rechnung and Auftragsbestätigung in DOCX and PDF format"""
    target_paths = {
        "rechnung": get_rechnung_target_path(project_dir, project_number, receipt_number),
        "auftrag": get_auftrag_target_path(project_dir, project_number, receipt_number)
    }
    render_rechnung_and_auftrag_docx(
        project_number,
        receipt_number,
        target_paths)
    render_pdf(target_paths["rechnung"])
    render_pdf(target_paths["auftrag"])
