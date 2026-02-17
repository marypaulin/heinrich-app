import logging
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from .calculations import calculate_sums_and_vat
from .config import Config
from .docgen import (
    fill_table_with_line_items,
    load_intermediate_template,
    load_template,
    replace_delivery_date,
    replace_placeholders,
    save_docx,
    save_intermediate_template,
)
from .messages import Messages
from .models import DocxDeliveryDate, DocxMeta, LineItem
from .paths import (
    get_delivery_target_path,
    get_invoice_target_path,
    get_offer_target_path,
    get_order_target_path,
)
from .pdfgen import render_pdf


def generate_offer_or_delivery_docx(
    doc_key: str,
    project_number: str,
    receipt_number: Optional[str],
    line_items: list[LineItem],
    target_path: Path,
    config: Config,
    messages: Messages,
    log_labels: tuple[str, str],
) -> None:
    """Fill Word template with CSV data and save as Angebot or Lieferschein DOCX."""

    doc = load_template()
    doc_config = config.documents[doc_key]

    # Set up meta data
    today = date.today()

    meta_data = DocxMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=doc_config.doctype,
        header=doc_config.header,
        date_today=today,
    )

    # Set up intermediate data
    totals = calculate_sums_and_vat(line_items, config)
    # Assert not None for type checking reasons
    assert doc_config.delivery_days is not None
    delivery_days = doc_config.delivery_days
    delivery_date = DocxDeliveryDate(today + timedelta(days=delivery_days))

    # Phase 1: Fill table with line items
    fill_table_with_line_items(doc, line_items)

    # Phase 2: Fill totals and delivery date + save intermediate template
    replace_placeholders(
        doc,
        totals.to_mapping(),
    )
    replace_delivery_date(doc, delivery_date.to_mapping(config.date_format))

    save_intermediate_template(project_number, doc)

    # Phase 3: Fill meta data + save final document
    replace_placeholders(
        doc,
        meta_data.to_mapping(config.date_format),
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

    doc_invoice = load_intermediate_template(project_number)
    doc_order = deepcopy(doc_invoice)

    config_invoice = config.documents["RECHNUNG"]
    config_order = config.documents["AUFTRAG"]

    # Set up meta data for invoice and order
    today = date.today()

    meta_invoice = DocxMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=config_invoice.doctype,
        header=config_invoice.header,
        date_today=today,
    )
    meta_order = DocxMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=config_order.doctype,
        header=config_order.header,
        date_today=today,
    )

    # Fill invoice placeholders + save
    replace_placeholders(
        doc_invoice,
        meta_invoice.to_mapping(config.date_format),
    )
    save_docx(doc_invoice, target_paths["invoice"])
    display_path = target_paths["invoice"].name
    logging.info(f"Generated invoice: {display_path}")
    messages.info(f"Rechnung erzeugt: {display_path}")

    # Fill order placeholders + save
    replace_placeholders(
        doc_order,
        meta_order.to_mapping(config.date_format),
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
        receipt_number=None,
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
    receipt_number: Optional[str],
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
        receipt_number=receipt_number,
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
