"""
Word document generation and PDF stub for heinrich-metallbau.
"""
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.table import _Row


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


def format_cell(cell, font_name="Calibri", font_size=10):
    """Set font for all text in a table cell."""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)


def _fill_table(doc: Document, data: List[Dict[str, str]]) -> None:
    """Fill the main table in the document with data."""
    # The table has 5 columns:
    # "Pos", "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # The first row of the table is the header row with these titles
    # Then we will have len(data) rows with the actual data
    # data is a list of dicts with keys: "Menge", "Beschreibung", "€/Stk", "Preis gesamt"
    # Each dict in data corresponds to one row in the table
    # "Pos" is just a running number starting from 1
    # "Menge" -> <Menge> (second column in table)
    # "Beschreibung" -> <Beschreibung> (third column in table)
    # "€/Stk" -> <€/Stk> (fourth column in table)
    # "Preis gesamt" -> <Preis gesamt> (fifth column in table)
    # Then we have a row with
    #   - Static string "Summe" in Pos + Menge columns (verbundene Zelle)
    #   - Placeholder <Summe> placeholder in "Preis gesamt" column which will be filled with the sum of all "Preis gesamt" values from data
    # Then we have a row with
    #   - "Ust. 19% auf <Summe> netto" in Pos + Menge + Beschreibung columns (verbundene Zelle)
    #   - Placeholder <Ust> in "Preis gesamt" column which will be filled with 19% of the sum
    # Then we have a row with
    #   - Static string "Gesamtbetrag" in Pos + Menge + Beschreibung columns
    #   - Placeholder <Gessumme> in "Preis gesamt" column which will be filled with sum + Ust
    if not doc.tables:
        logging.warning("No tables found in the document to fill.")
        return
    for table in doc.tables:
        if len(table.columns) == 5 and table.cell(0, 0).text == "Pos":
            target_table = table
            # Find where the summary rows start (last 3 rows)
            FOOTER_ROWS = 3  # MwSt/Summe block at the end

            # Fill the first data row (already present in template)
            if data:
                row = target_table.rows[1]
                cells = row.cells
                cells[0].text = str(1)
                cells[1].text = data[0].get("Menge", "")
                cells[2].text = data[0].get("Beschreibung", "")
                cells[3].text = data[0].get("€/Stk", "") + "€"
                cells[4].text = data[0].get("Preis gesamt", "") + "€"

                # Format all cells in this row
                for cell in cells:
                    format_cell(cell)

                # Letzte Spalte rechtsbündig
                cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # For additional data rows, insert new rows
            for pos, row_data in enumerate(data[1:], start=2):
                # 1) Create a new row (style taken from the current last row)
                row = target_table.add_row()
                tr = row._tr
                tbl = target_table._tbl

                # 2) Compute insertion index: just before the footer block
                insert_at = len(target_table.rows) - FOOTER_ROWS + 1

                # 3) Move the row's XML node to the desired position
                tbl.remove(tr)          # Detach from end
                tbl.insert(insert_at, tr)  # Re-insert before footers

                # 4) Rewrap so the proxy matches the new position
                row = _Row(tr, target_table)

                # 5) Fill cells
                cells = row.cells
                cells[0].text = str(pos)
                cells[1].text = row_data.get("Menge", "")
                cells[2].text = row_data.get("Beschreibung", "")
                cells[3].text = row_data.get("€/Stk", "") + "€"
                cells[4].text = row_data.get("Preis gesamt", "") + "€"

                # 6) Format all cells in this row
                for cell in cells:
                    format_cell(cell)

                # 7) Letzte Spalte rechtsbündig
                cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            break
        else:
            continue

def render_lieferschein(template_path: Path, project_number: str, data: List[Dict[str, str]], output_path: Path) -> None:
    """Fill the Word template with CSV data and save as Lieferschein."""
    doc = Document(template_path)
    current_date = date.today().strftime("%d.%m.%Y")
    receipt_number = ""
    doctype = "Lieferschein"
    header = "Wir liefern folgende Positionen an:"
    deliver_date = (date.today() + timedelta(days=21)).strftime("%d.%m.%Y")

    # Placeholder mapping
    mapping = {
        "<Datum heute>": current_date,
        "<Lfd Nr.>": project_number,
        "<Belegnr>": receipt_number,
        "<Betreffart>": doctype,
        "<Header>": header,
        "<Datum heute + 21 Tage>": deliver_date,
    }

    _replace_placeholders(doc, mapping)
    _fill_table(doc, data)

    doc.save(output_path)
    logging.info(f"Generated Word document: {output_path}")


def render_pdf_stub(pdf_path: Path) -> None:
    """Stub for PDF generation from DOCX."""
    # TODO: Implement real DOCX to PDF conversion
    with open(pdf_path, 'w') as f:
        f.write('PDF generation not implemented yet.')
    logging.info(f"Stub PDF created: {pdf_path}")
