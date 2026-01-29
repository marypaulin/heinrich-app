import logging
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from .calculations import calculate_sums_and_vat
from .config import Config
from .docgen import (
    fill_table_with_line_items,
    load_intermediate_template,
    load_template,
    replace_placeholders,
    save_docx,
)
from .formatting import format_price
from .messages import Messages
from .models import DocMeta, IntermediateData, LineItem
from .paths import (
    get_auftrag_target_path,
    get_intermediate_rechnung_path,
    get_liefer_target_path,
    get_rechnung_target_path,
)
from .pdfgen import render_pdf

PH_DATE_TODAY = "<Datum heute>"
PH_PROJECT_NO = "<Lfd Nr.>"
PH_RECEIPT_NO = "<Belegnr>"
PH_DOCTYPE = "<Betreffart>"
PH_HEADER = "<Header>"

PH_SUM_NET = "<Summe>"
PH_VAT = "<Ust>"
PH_SUM_GROSS = "<Gessumme>"
PH_DELIVERY_DATE = "<Datum heute + 21 Tage>"


def build_meta_mapping(data: DocMeta, config: Config) -> Dict[str, str]:
    return {
        PH_DATE_TODAY: data.date_today.strftime(config.date_format),
        PH_PROJECT_NO: data.project_number,
        PH_RECEIPT_NO: data.receipt_number or "",
        PH_DOCTYPE: data.doctype,
        PH_HEADER: data.header,
    }


def build_intermediate_mapping(
    data: IntermediateData, config: Config
) -> Dict[str, str]:
    t = data.totals
    return {
        PH_SUM_NET: format_price(t.sum_net),
        PH_VAT: format_price(t.vat),
        PH_SUM_GROSS: format_price(t.sum_gross),
        PH_DELIVERY_DATE: data.delivery_date.strftime(config.date_format),
    }


def render_lieferschein_docx(
    project_number: str,
    line_items: List[LineItem],
    target_path: Path,
    config: Config,
    messages: Messages,
) -> None:
    """Fill the Word template with CSV data and save as Lieferschein DOCX."""

    doc = load_template()
    doc_config = config.documents["LIEFERSCHEIN"]

    # Set up meta data for Lieferschein
    today = date.today()

    meta_data = DocMeta(
        project_number=project_number,
        receipt_number=None,
        doctype=doc_config.doctype,
        header=doc_config.header,
        date_today=today,
    )

    # Set up intermediate data
    totals = calculate_sums_and_vat(line_items, config)
    delivery_days = doc_config.delivery_days or 21
    delivery_date = today + timedelta(days=delivery_days)

    intermediate_data = IntermediateData(
        totals=totals,
        delivery_date=delivery_date,
    )

    # Phase 1: Fill table with line items
    fill_table_with_line_items(doc, line_items)

    # Phase 2: Fill intermediate placeholders + save intermediate template
    replace_placeholders(
        doc,
        build_intermediate_mapping(intermediate_data, config),
    )

    intermediate_path = get_intermediate_rechnung_path(project_number)
    intermediate_path.parent.mkdir(parents=True, exist_ok=True)
    save_docx(doc, intermediate_path)

    # Phase 3: Fill Lieferschein placeholders + save final
    replace_placeholders(
        doc,
        build_meta_mapping(meta_data, config),
    )

    save_docx(doc, target_path)

    display_path = target_path.name
    logging.info(f"Generated Lieferschein: {display_path}")
    messages.info(f"Lieferschein erzeugt: {display_path}")


def render_rechnung_and_auftrag_docx(
    project_number: str,
    receipt_number: str,
    target_paths: Dict[str, Path],
    config: Config,
    messages: Messages,
) -> None:
    """Generate Rechnung and Auftragsbestaetigung DOCX from intermediate template."""

    intermediate_path = get_intermediate_rechnung_path(project_number)
    doc = load_intermediate_template(intermediate_path)

    doc_rechnung = deepcopy(doc)
    doc_auftrag = deepcopy(doc)

    rechnung_config = config.documents["RECHNUNG"]
    auftrag_config = config.documents["AUFTRAG"]

    # Set up meta data for Rechnung and Auftragsbestätigung
    today = date.today()

    meta_rechnung = DocMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=rechnung_config.doctype,
        header=rechnung_config.header,
        date_today=today,
    )
    meta_auftrag = DocMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=auftrag_config.doctype,
        header=auftrag_config.header,
        date_today=today,
    )

    # Fill Rechnung placeholders + save
    replace_placeholders(
        doc_rechnung,
        build_meta_mapping(meta_rechnung, config),
    )
    save_docx(doc_rechnung, target_paths["rechnung"])
    display_path = target_paths["rechnung"].name
    logging.info(f"Generated Rechnung: {display_path}")
    messages.info(f"Rechnung erzeugt: {display_path}")

    # Fill Auftragsbestätigung placeholders + save
    replace_placeholders(
        doc_auftrag,
        build_meta_mapping(meta_auftrag, config),
    )
    save_docx(doc_auftrag, target_paths["auftrag"])
    display_path = target_paths["auftrag"].name
    logging.info(f"Generated Auftragsbestätigung: {display_path}")
    messages.info(f"Auftragsbestätigung erzeugt: {display_path}")


def render_lieferschein(
    project_number: str,
    line_items: List[LineItem],
    project_dir: Path,
    config: Config,
) -> list[str]:
    """Render Lieferschein in DOCX and PDF format"""
    messages = Messages()
    target_path = get_liefer_target_path(project_dir, project_number, config)
    render_lieferschein_docx(
        project_number,
        line_items,
        target_path,
        config,
        messages,
    )
    render_pdf(target_path, messages)
    return messages.items


def render_rechnung_and_auftrag(
    project_number: str,
    receipt_number: str,
    project_dir: Path,
    config: Config,
) -> list[str]:
    """Render Rechnung and Auftragsbestätigung in DOCX and PDF format"""
    messages = Messages()
    rechnung_path = get_rechnung_target_path(
        project_dir,
        project_number,
        receipt_number,
        config,
    )
    auftrag_path = get_auftrag_target_path(
        project_dir,
        project_number,
        receipt_number,
        config,
    )
    target_paths = {
        "rechnung": rechnung_path,
        "auftrag": auftrag_path,
    }
    render_rechnung_and_auftrag_docx(
        project_number,
        receipt_number,
        target_paths,
        config,
        messages,
    )
    render_pdf(rechnung_path, messages)
    render_pdf(auftrag_path, messages)
    return messages.items
