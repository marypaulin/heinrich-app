import logging
import platform
import shutil
import subprocess
from pathlib import Path

from docx2pdf import convert


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
                logging.info(
                    f"Generated PDF document via LibreOffice: {pdf_path}")
                return
            except subprocess.CalledProcessError as e:
                logging.error(f"LibreOffice PDF conversion failed: {e}")
                return

    # If no supported system or conversion failed
    logging.error(
        "PDF generation not supported. "
        "Please install Microsoft Word (on Windows) or LibreOffice (on Linux)."
    )
