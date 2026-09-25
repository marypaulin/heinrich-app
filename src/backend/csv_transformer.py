"""CSV row transformation into document-ready LineItem objects."""

import logging
from collections.abc import Iterable

from .config import Config
from .messages import Messages
from .models import CsvRow, LineItem


def _get_hourly_description(
    hourly_rate: float, config: Config, messages: Messages
) -> str:
    """Get description based on hourly rate"""
    if hourly_rate in config.hourly_rate_mapping:
        return config.hourly_rate_mapping[hourly_rate]
    logging.warning(
        f"Unknown hourly rate {hourly_rate}, using default description '{config.hourly_rate_default}'"
    )
    messages.warning(
        f"Unbekannter Stundenlohn {hourly_rate}, "
        f"nutze Default '{config.hourly_rate_default}'"
    )
    return config.hourly_rate_default


def _hours_item(csv_row: CsvRow, config: Config, messages: Messages) -> LineItem:
    logging.info(f"Creating hours item for order number: {csv_row.order_number}")
    hourly_description = _get_hourly_description(csv_row.hourly_rate, config, messages)
    return LineItem(
        kind="hours",
        order_number=csv_row.order_number,
        quantity=csv_row.duration_hours,
        description=f"{hourly_description} zu Auftrag Nr. {csv_row.order_number}",
        unit_price=csv_row.hourly_rate,
        total_price=csv_row.hourly_rate * csv_row.duration_hours,
    )


def _material_item(csv_row: CsvRow) -> LineItem:
    logging.info(f"Creating material item for order number: {csv_row.order_number}")
    return LineItem(
        kind="material",
        order_number=csv_row.order_number,
        quantity=1.0,
        # NOTE: Original CSV description currently not used upon customer request
        description=f"Material zu Auftrag Nr. {csv_row.order_number}",
        unit_price=csv_row.material_cost,
        total_price=csv_row.material_cost,
    )


def csv_rows_to_line_items(
    csv_rows: Iterable[CsvRow],
    config: Config,
) -> tuple[list[LineItem], list[str]]:
    """
    Transform CsvRow objects into LineItem domain objects.

    This function contains the business logic for converting raw CSV data
    into document-ready line items.

    Transformation rules:
    - Each valid CsvRow always produces one "hours" LineItem.
    - If material_cost is non-zero, an additional "material" LineItem
      is created.
    - LineItems are enriched with calculated totals and derived descriptions.

    Data lineage:
    - Hours LineItem:
        quantity    <- CsvRow.duration_hours
        unit_price  <- CsvRow.hourly_rate
        total_price <- hourly_rate * duration
    - Material LineItem:
        quantity    <- 1
        unit_price  <- CsvRow.material_cost
        total_price <- material_cost

    Validation and filtering:
    - Rows without an order number are skipped.
    - All numeric values are assumed to be already parsed and validated
      in the CSV loader.

    Parameters:
        csv_rows: Iterable of parsed CsvRow objects.
        config: Application configuration (hourly rate descriptions, defaults).

    Returns:
        A list of LineItem objects ready for document generation or export.
        A list of info and warning messages to display in UI.
    """
    messages = Messages()
    result = []
    for csv_row in csv_rows:
        if not csv_row.order_number:
            logging.info(f"Skipping csv_row {csv_row.row_number} without order number")
            messages.warning(
                f"Überspringe Zeile {csv_row.row_number}: Keine Auftrags-Nr. angegeben."
            )
            continue

        result.append(_hours_item(csv_row, config, messages))
        if csv_row.material_cost != 0:
            result.append(_material_item(csv_row))

    return result, messages.items
