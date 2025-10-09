"""
Word document generation and PDF stub for heinrich-metallbau.
"""
import logging
import platform
import shutil
import subprocess
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from docx import Document
from docx2pdf import convert
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.table import _Row


def format_duration(value: float) -> str:
    """Format a duration value with one decimal, German locale (e.g. 1.5 -> 1,5; 2.0 -> 2)."""
    if value % 1 == 0:
        return str(int(value))
    return f"{value:.1f}".replace(".", ",")


def format_price(value: float) -> str:
    """Format a price value with thousands separator and two decimals, German locale (e.g. 1234.5 -> 1.234,50 €)."""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "€"


def _calculate_sums_and_vat(data: List[Dict[str, str | int | float]]) -> Tuple[float, float, float]:
    """Calculate sum_net, vat (19%), and sum_vat."""
    sum_net = 0.0
    for row in data:
        total_price = row.get("Preis gesamt", "0")
        sum_net += total_price
    vat = sum_net * 0.19
    sum_vat = sum_net + vat
    return sum_net, vat, sum_vat


def _replace_placeholders(doc: Document, mapping: Dict[str, str]) -> None:
    """Replace placeholders in all paragraphs of the document."""
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for placeholder, value in mapping.items():
                if placeholder in run.text:
                    run.text = run.text.replace(placeholder, value)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        for placeholder, value in mapping.items():
                            if placeholder in run.text:
                                run.text = run.text.replace(placeholder, value)


def format_cell(cell, font_name="Calibri", font_size=9, bold=True):
    """Set font for all text in a table cell."""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = bold


def _fill_table(doc: Document, data: List[Dict[str, str]]) -> None:
    """Fill the main table in the document with data."""
    # The table has 5 columns:
    # "Pos", "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # The first row of the table is the header row with these titles
    # Then we will have len(data) rows with the actual data
    # data is a list of dicts with keys: "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # Each dict in data corresponds to one row in the table
    # "Pos" is just a running number starting from 1
    # "Menge" -> <Menge> (second column)
    # "Beschreibung" -> <Beschreibung> (third column)
    # "€/Stk" -> <€/Stk> (fourth column)
    # "Preis gesamt" -> <Preis gesamt> (fifth column)
    if not doc.tables:
        logging.warning("No tables found in the document to fill.")
        return
    for table in doc.tables:
        if len(table.columns) == 5 and table.cell(0, 0).text == "Pos":
            target_table = table

            # Fill the first data row (already present in template)
            if data:
                # 1) Get the first table row
                row = target_table.rows[1]

                # 2) Fill cells
                cells = row.cells
                cells[0].text = str(1)
                cells[1].text = format_duration(float(data[0].get("Menge", "")))
                # Only take the part before the first " (" (if present)
                description_full = str(data[0].get("Beschreibung", ""))
                description_main = description_full.split(" (")[0]
                cells[2].text = description_main
                cells[3].text = format_price(float(data[0].get('€/Stk', 0)))
                cells[4].text = format_price(float(data[0].get('Preis gesamt', 0)))

                # 3) Format all cells in this row
                for cell in cells:
                    format_cell(cell)

                # 4) Align last two columns to the right
                cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # For additional data rows, insert new rows
            for pos, row_data in enumerate(data[1:], start=2):
                # 1) Create a new row
                tr = deepcopy(target_table.rows[1]._tr)
                tbl = target_table._tbl

                # 2) Compute insertion index
                insert_at = pos + 2

                # 3) Insert the row's XML node to the desired position
                tbl.insert(insert_at, tr)

                # 4) Rewrap so the proxy matches the new position
                row = _Row(tr, target_table)

                # 5) Fill cells
                cells = row.cells
                cells[0].text = str(pos)
                cells[1].text = format_duration(float(row_data.get("Menge", "")))
                # Only take the part before the first " (" (if present)
                description_full = str(row_data.get("Beschreibung", ""))
                description_main = description_full.split(" (")[0]
                cells[2].text = description_main
                cells[3].text = format_price(float(row_data.get('€/Stk', 0)))
                cells[4].text = format_price(float(row_data.get('Preis gesamt', 0)))

                # 6) Format all cells in this row
                for cell in cells:
                    format_cell(cell)

                # 7) Align last two columns to the right
                cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            break
        else:
            continue

def render_lieferschein(
        template_path: Path,
        project_number: str,
        data: List[Dict[str, str | int | float]],
        rechnung_template_path: Path,
        output_path: Path) -> None:
    """Fill the Word template with CSV data and save as Lieferschein."""
    doc = Document(template_path)

    # Set up fixed placeholders
    current_date = date.today().strftime("%d.%m.%Y")
    receipt_number = ""
    doctype = "Lieferschein"
    header = "Wir liefern folgende Positionen an:"
    deliver_date = (date.today() + timedelta(days=21)).strftime("%d.%m.%Y")

    # Calculate sums and vat
    sum_net, vat, sum_gross = _calculate_sums_and_vat(data)

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

    _fill_table(doc, data)
    _replace_placeholders(doc, mapping_sum)

    # Save intermediate document for Rechnung template use
    doc.save(rechnung_template_path)

    _replace_placeholders(doc, mapping_liefer)

    doc.save(output_path)
    logging.info(f"Generated Word document: {output_path}")


def render_rechnung_and_auftrag(
        template_path: Path,
        project_number: str,
        receipt_number: str,
        output_paths: Dict[str, Path]) -> None:
    """Generate Rechnung and Auftragsbestaetigung from template."""

    # Load the generated template for Rechnung and Auftragsbestätigung
    doc = Document(template_path)
    # Make two independent copies of the loaded document
    doc_rechnung = deepcopy(doc)
    doc_auftrag = deepcopy(doc)

    # Set up fixed placeholders
    current_date = date.today().strftime("%d.%m.%Y")
    receipt_number = receipt_number
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
    _replace_placeholders(doc_rechnung, mapping_rechnung)
    doc_rechnung.save(output_paths["rechnung"])
    logging.info(f"Generated Word document: {output_paths["rechnung"]}")

    # Replace placeholders for Auftragsbestätigung
    _replace_placeholders(doc_auftrag, mapping_auftrag)
    doc_auftrag.save(output_paths["auftrag"])
    logging.info(f"Generated Word document: {output_paths["auftrag"]}")


def render_pdf(docx_path: Path) -> None:
    """Convert DOCX file to PDF using Word on Windows or LibreOffice on Linux."""

    # Derive output PDF path from the DOCX path
    pdf_path = docx_path.with_suffix(".pdf")
    system = platform.system()

    if system == "Windows":
        # Use Microsoft Word via docx2pdf for perfect formatting
        try:
            convert(str(docx_path), str(pdf_path))
            logging.info(f"Generated PDF document via Word: {pdf_path}")
            return
        except Exception as e:
            logging.error(f"Word-based PDF conversion failed: {e}")
            return

    elif system == "Linux":
        # Use LibreOffice headless mode as fallback
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            try:
                subprocess.run(
                    [
                        soffice,
                        "--headless",
                        "--nologo",
                        "--nodefault",
                        "--nofirststartwizard",
                        "--convert-to", "pdf",
                        "--outdir", str(pdf_path.parent),
                        str(docx_path)],
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logging.info(f"Generated PDF document via LibreOffice: {pdf_path}")
                return
            except subprocess.CalledProcessError as e:
                logging.error(f"LibreOffice PDF conversion failed: {e}")
                return

    # If no supported system or conversion failed
    logging.error(
        "PDF generation not supported. "
        "Please install Microsoft Word (on Windows) or LibreOffice (on Linux)."
    )
