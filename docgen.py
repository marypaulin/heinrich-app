"""
Word document generation and PDF stub for heinrich-metallbau.
"""
import logging
from pathlib import Path
from typing import Dict, List

from docx import Document

from paths import get_output_paths


def render_lieferschein(template_path: Path, data: List[Dict[str, str]], output_path: Path) -> None:
    """Fill the Word template with CSV data and save as Lieferschein."""
    doc = Document(template_path)
    # TODO: Map CSV data to template placeholders
    # Example: for p in doc.paragraphs: ...
    doc.save(output_path)
    logging.info(f"Generated Word document: {output_path}")


def render_pdf_stub(pdf_path: Path) -> None:
    """Stub for PDF generation from DOCX."""
    # TODO: Implement real DOCX to PDF conversion
    with open(pdf_path, 'w') as f:
        f.write('PDF generation not implemented yet.')
    logging.info(f"Stub PDF created: {pdf_path}")
