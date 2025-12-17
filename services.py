import logging
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from calculations import calculate_sums_and_vat
from core.config import Config
from docgen import (fill_table_with_line_items, load_intermediate_template,
                    load_template, replace_placeholders, save_docx)
from formatting import format_price
from models import LineItem
from paths import (get_auftrag_target_path, get_intermediate_rechnung_path,
                   get_liefer_target_path, get_rechnung_target_path)
from pdfgen import render_pdf


def render_lieferschein_docx(
        project_number: str,
        line_items: List[LineItem],
        target_path: Path,
        config: Config) -> None:
    """Fill the Word template with CSV data and save as Lieferschein DOCX."""
    doc = load_template()

    # Set up fixed placeholders
    current_date = date.today().strftime("%d.%m.%Y")
    receipt_number = ""
    doctype = "Lieferschein"
    header = "Wir liefern folgende Positionen an:"
    deliver_date = (date.today() + timedelta(days=21)).strftime("%d.%m.%Y")

    # Calculate sums and vat
    sum_net, vat, sum_gross = calculate_sums_and_vat(line_items, config)

    # Placeholder mappings
    mapping_liefer = {
        "<Datum heute>": current_date,
        "<Lfd Nr.>": project_number,
        "<Belegnr>": receipt_number,
        "<Betreffart>": doctype,
        "<Header>": header
    }
    mapping_sum = {
        "<Summe>": format_price(sum_net),
        "<Ust>": format_price(vat),
        "<Gessumme>": format_price(sum_gross),
        "<Datum heute + 21 Tage>": deliver_date,
    }

    fill_table_with_line_items(doc, line_items)
    replace_placeholders(doc, mapping_sum)

    # Save intermediate document for Rechnung template use
    intermediate_path = get_intermediate_rechnung_path(project_number)
    intermediate_path.parent.mkdir(parents=True, exist_ok=True)
    save_docx(doc, intermediate_path)

    replace_placeholders(doc, mapping_liefer)

    save_docx(doc, target_path)
    logging.info(f"Generated Lieferschein: {target_path}")


def render_rechnung_and_auftrag_docx(
        project_number: str,
        receipt_number: str,
        target_paths: Dict[str, Path]) -> None:
    """Generate Rechnung and Auftragsbestaetigung DOCX from intermediate template."""

    # Load the generated template for Rechnung and Auftragsbestätigung
    intermediate_path = get_intermediate_rechnung_path(project_number)
    doc = load_intermediate_template(intermediate_path)
    # Make two independent copies of the loaded document
    doc_rechnung = deepcopy(doc)
    doc_auftrag = deepcopy(doc)

    # Set up fixed placeholders
    current_date = date.today().strftime("%d.%m.%Y")
    doctype_rechnung = "Rechnung"
    doctype_auftrag = "Auftragsbestätigung"
    header_rechnung = "Wir bitten um Ausgleich der folgenden Positionen:"
    header_auftrag = "Wir bestätigen den Auftrag über folgende Positionen:"

    # Placeholder mappings
    mapping_rechnung = {
        "<Datum heute>": current_date,
        "<Lfd Nr.>": project_number,
        "<Belegnr>": receipt_number,
        "<Betreffart>": doctype_rechnung,
        "<Header>": header_rechnung
    }
    mapping_auftrag = {
        "<Datum heute>": current_date,
        "<Lfd Nr.>": project_number,
        "<Belegnr>": receipt_number,
        "<Betreffart>": doctype_auftrag,
        "<Header>": header_auftrag
    }

    # Replace placeholders for Rechnung
    replace_placeholders(doc_rechnung, mapping_rechnung)
    save_docx(doc_rechnung, target_paths["rechnung"])
    logging.info(f"Generated Rechnung: {target_paths['rechnung']}")

    # Replace placeholders for Auftragsbestätigung
    replace_placeholders(doc_auftrag, mapping_auftrag)
    save_docx(doc_auftrag, target_paths["auftrag"])
    logging.info(f"Generated Auftragsbestätigung: {target_paths['auftrag']}")


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
