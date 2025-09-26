"""
Word document generation and PDF stub for heinrich-metallbau.
"""
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from docx import Document


def _replace_placeholders(doc: Document, mapping: Dict[str, str]) -> None:
    """Replace placeholders in all paragraphs of the document."""
    for paragraph in doc.paragraphs:
        for placeholder, value in mapping.items():
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, value)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in mapping.items():
                        if placeholder in paragraph.text:
                            paragraph.text = paragraph.text.replace(placeholder, value)

def _fill_table(doc: Document, data: List[Dict[str, str]]) -> None:
    """Fill the second table in the document with data."""
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
    table = doc.tables[1]
    # TODO: Fill table with data

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
