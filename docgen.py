"""
Word document generation and PDF stub for heinrich-metallbau.
"""
import logging
from pathlib import Path
from typing import Dict, List

from docx import Document


def render_lieferschein(template_path: Path, data: List[Dict[str, str]], project_number: str) -> Path:
    """Fill the Word template with CSV data and save as Lieferschein."""
    doc = Document(template_path)
    # TODO: Map CSV data to template placeholders
    # Example: for p in doc.paragraphs: ...
    output_path = Path(f"Lieferschein Nr. {project_number}.docx")
    doc.save(output_path)
    logging.info(f"Generated Word document: {output_path}")
    return output_path


def render_pdf_stub(docx_path: Path) -> None:
    """Stub for PDF generation from DOCX."""
    pdf_path = docx_path.with_suffix('.pdf')
    # TODO: Implement real DOCX to PDF conversion
    with open(pdf_path, 'w') as f:
        f.write('PDF generation not implemented yet.')
    logging.info(f"Stub PDF created: {pdf_path}")
