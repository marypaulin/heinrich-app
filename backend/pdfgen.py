import contextlib
import logging
import platform
import shutil
import subprocess
import threading
from pathlib import Path

from docx2pdf import convert

from .messages import Messages

# Ensure Word conversion runs strictly one-at-a-time (Streamlit reruns / double clicks can parallelize)
_WORD_CONVERT_LOCK = threading.Lock()


def render_pdf(docx_path: Path, messages: Messages) -> None:
    """Convert DOCX file to PDF using Word on Windows or LibreOffice on Linux."""

    pdf_path = docx_path.with_suffix(".pdf")
    system = platform.system()

    # --------------------
    # Windows: Microsoft Word via docx2pdf
    # --------------------
    if system == "Windows":
        # Most common failure: existing/open PDF blocks overwrite
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except PermissionError:
                messages.error(
                    f"PDF konnte nicht überschrieben werden (Datei evtl. geöffnet): {pdf_path.name}"
                )
                logging.exception("PDF locked / cannot delete: %s", pdf_path)
                return

        # COM init is required per-thread on Windows. Streamlit may execute in a thread without COM initialized.
        try:
            import pythoncom  # type: ignore  # provided by pywin32
        except Exception:
            pythoncom = None

        try:
            with _WORD_CONVERT_LOCK:
                if pythoncom is not None:
                    pythoncom.CoInitialize()

                # More robust: output directory instead of output file
                convert(str(docx_path), str(docx_path.parent))

                # docx2pdf can fail silently -> verify output exists
                if not pdf_path.exists():
                    messages.error(
                        "PDF wurde nicht erzeugt. "
                        "Bitte prüfen: Word installiert, Datei nicht geöffnet, "
                        "keine hängende WINWORD.EXE."
                    )
                    logging.error(
                        "docx2pdf finished without creating pdf: %s", pdf_path
                    )
                    return

            messages.info(f"PDF erzeugt: {pdf_path.name}")
            logging.info("Generated PDF document via Word: %s", pdf_path.name)
            return

        except Exception as e:
            messages.error(f"PDF-Erzeugung fehlgeschlagen: {e}")
            logging.exception("Word-based PDF conversion failed")
            return

        finally:
            if pythoncom is not None:
                with contextlib.suppress(Exception):
                    pythoncom.CoUninitialize()

    # --------------------
    # Linux: LibreOffice (headless)
    # --------------------
    elif system == "Linux":
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            messages.error(
                "LibreOffice nicht gefunden. Bitte LibreOffice installieren."
            )
            logging.error("LibreOffice (soffice) not found")
            return

        try:
            subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--nologo",
                    "--nodefault",
                    "--nofirststartwizard",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(docx_path.parent),
                    str(docx_path),
                ],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if not pdf_path.exists():
                messages.error(
                    "PDF wurde nicht erzeugt. LibreOffice-Konvertierung fehlgeschlagen."
                )
                logging.error("LibreOffice finished without creating pdf: %s", pdf_path)
                return

            messages.info(f"PDF erzeugt: {pdf_path.name}")
            logging.info("Generated PDF document via LibreOffice: %s", pdf_path.name)
            return

        except subprocess.CalledProcessError as e:
            messages.error(f"LibreOffice PDF-Erzeugung fehlgeschlagen: {e}")
            logging.exception("LibreOffice PDF conversion failed")
            return

    # --------------------
    # Unsupported system
    # --------------------
    messages.error("PDF-Erzeugung wird auf diesem Betriebssystem nicht unterstützt.")
    logging.error("PDF generation not supported on system: %s", system)
