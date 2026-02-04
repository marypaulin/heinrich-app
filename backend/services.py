import logging
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

from .calculations import calculate_sums_and_vat
from .config import Config
from .docgen import (
    fill_table_with_line_items,
    load_intermediate_template,
    load_template,
    replace_delivery_date,
    replace_placeholders,
    save_docx,
)
from .formatting import format_price
from .messages import Messages
from .models import DocMeta, LineItem, Totals
from .paths import (
    get_delivery_target_path,
    get_intermediate_invoice_path,
    get_invoice_target_path,
    get_offer_target_path,
    get_order_target_path,
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
PH_DELIVERY_DATE = "<Lieferdatum>"


def build_meta_mapping(data: DocMeta, config: Config) -> dict[str, str]:
    return {
        PH_DATE_TODAY: data.date_today.strftime(config.date_format),
        PH_PROJECT_NO: data.project_number,
        PH_RECEIPT_NO: data.receipt_number or "",
        PH_DOCTYPE: data.doctype,
        PH_HEADER: data.header,
    }


def build_totals_mapping(totals: Totals) -> dict[str, str]:
    return {
        PH_SUM_NET: format_price(totals.sum_net),
        PH_VAT: format_price(totals.vat),
        PH_SUM_GROSS: format_price(totals.sum_gross),
    }


def build_delivery_date_mapping(delivery_date: date, config: Config) -> dict[str, str]:
    return {
        PH_DELIVERY_DATE: delivery_date.strftime(config.date_format),
    }


def generate_offer_or_delivery_docx(
    doc_key: str,
    project_number: str,
    line_items: list[LineItem],
    target_path: Path,
    config: Config,
    messages: Messages,
    log_labels: tuple[str, str],
) -> None:
    """Fill Word template with CSV data and save as Angebot or Lieferschein DOCX."""

    doc = load_template()
    doc_config = config.documents[doc_key]

    # Set up meta data for delivery note
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
    d = doc_config.delivery_days
    delivery_days = d if d is not None else 21
    delivery_date = today + timedelta(days=delivery_days)

    # Phase 1: Fill table with line items
    fill_table_with_line_items(doc, line_items)

    # Phase 2: Fill intermediate data + save intermediate template
    replace_placeholders(
        doc,
        build_totals_mapping(totals),
    )
    replace_delivery_date(doc, build_delivery_date_mapping(delivery_date, config))

    intermediate_path = get_intermediate_invoice_path(project_number)
    intermediate_path.parent.mkdir(parents=True, exist_ok=True)
    save_docx(doc, intermediate_path)

    # Phase 3: Fill final placeholders + save final document
    replace_placeholders(
        doc,
        build_meta_mapping(meta_data, config),
    )

    save_docx(doc, target_path)

    display_path = target_path.name
    logging.info(f"Generated {log_labels[0]}: {display_path}")
    messages.info(f"{log_labels[1]} erzeugt: {display_path}")


def generate_invoice_and_order_docx(
    project_number: str,
    receipt_number: str,
    target_paths: dict[str, Path],
    config: Config,
    messages: Messages,
) -> None:
    """Generate Rechnung and Auftragsbestaetigung DOCX from intermediate template."""

    intermediate_path = get_intermediate_invoice_path(project_number)
    doc = load_intermediate_template(intermediate_path)

    doc_invoice = deepcopy(doc)
    doc_order = deepcopy(doc)

    config_invoice = config.documents["RECHNUNG"]
    config_order = config.documents["AUFTRAG"]

    # Set up meta data for invoice and order
    today = date.today()

    meta_invoice = DocMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=config_invoice.doctype,
        header=config_invoice.header,
        date_today=today,
    )
    meta_order = DocMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=config_order.doctype,
        header=config_order.header,
        date_today=today,
    )

    # Fill invoice placeholders + save
    replace_placeholders(
        doc_invoice,
        build_meta_mapping(meta_invoice, config),
    )
    save_docx(doc_invoice, target_paths["invoice"])
    display_path = target_paths["invoice"].name
    logging.info(f"Generated invoice: {display_path}")
    messages.info(f"Rechnung erzeugt: {display_path}")

    # Fill order placeholders + save
    replace_placeholders(
        doc_order,
        build_meta_mapping(meta_order, config),
    )
    save_docx(doc_order, target_paths["order"])
    display_path = target_paths["order"].name
    logging.info(f"Generated order confirmation: {display_path}")
    messages.info(f"Auftragsbestätigung erzeugt: {display_path}")


def generate_offer(
    project_number: str,
    line_items: list[LineItem],
    project_dir: Path,
    config: Config,
) -> list[str]:
    """Render Angebot in DOCX and PDF format"""
    messages = Messages()
    target_path = get_offer_target_path(project_dir, project_number, config)
    generate_offer_or_delivery_docx(
        doc_key="ANGEBOT",
        project_number=project_number,
        line_items=line_items,
        target_path=target_path,
        config=config,
        messages=messages,
        log_labels=("offer", "Angebot"),
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_delivery(
    project_number: str,
    line_items: list[LineItem],
    project_dir: Path,
    config: Config,
) -> list[str]:
    """Render Lieferschein in DOCX and PDF format"""
    messages = Messages()
    target_path = get_delivery_target_path(project_dir, project_number, config)
    generate_offer_or_delivery_docx(
        doc_key="LIEFERSCHEIN",
        project_number=project_number,
        line_items=line_items,
        target_path=target_path,
        config=config,
        messages=messages,
        log_labels=("delivery note", "Lieferschein"),
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_invoice_and_order(
    project_number: str,
    receipt_number: str,
    project_dir: Path,
    config: Config,
) -> list[str]:
    """Render Rechnung and Auftragsbestätigung in DOCX and PDF format"""
    messages = Messages()
    invoice_path = get_invoice_target_path(
        project_dir,
        project_number,
        receipt_number,
        config,
    )
    order_path = get_order_target_path(
        project_dir,
        project_number,
        receipt_number,
        config,
    )
    target_paths = {
        "invoice": invoice_path,
        "order": order_path,
    }
    generate_invoice_and_order_docx(
        project_number,
        receipt_number,
        target_paths,
        config,
        messages,
    )
    render_pdf(invoice_path, messages)
    render_pdf(order_path, messages)
    return messages.items
