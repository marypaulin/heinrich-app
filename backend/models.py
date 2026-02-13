from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional

from .formatting import format_price
from .placeholders import (
    PH_DATE_TODAY,
    PH_DELIVERY_DATE,
    PH_DOCTYPE,
    PH_HEADER,
    PH_PROJECT_NO,
    PH_RECEIPT_NO,
    PH_SUM_GROSS,
    PH_SUM_NET,
    PH_VAT,
)


@dataclass
class CsvRow:
    row_number: int  # For debugging
    date: date  # "Datum" - aus "%d.%m.%Y" geparst
    order_number: str  # "Auftrags-Nr."
    description: str  # "Beschreibung"
    duration_hours: float  # "Dauer (Std)"
    hourly_rate: float  # "Stundensatz (€)"
    material_cost: float  # "Material (€)"
    total_cost: float  # "Gesamtkosten (€)" - just for debugging


@dataclass
class LineItem:
    # CSV rows split into two kinds
    kind: Literal["hours", "material"]
    order_number: str  # "Auftrag Nr."
    quantity: float  # "Menge"
    description: str  # "Beschreibung"
    unit_price: float  # "€/Stk"
    total_price: float  # "Preis gesamt" = €/Stk * Menge


@dataclass(frozen=True)
class Totals:
    sum_net: float
    vat: float
    sum_gross: float

    def to_mapping(self) -> dict[str, str]:
        return {
            PH_SUM_NET: format_price(self.sum_net),
            PH_VAT: format_price(self.vat),
            PH_SUM_GROSS: format_price(self.sum_gross),
        }


@dataclass(frozen=True)
class DocxMeta:
    project_number: str
    receipt_number: Optional[str]
    doctype: str
    header: str
    date_today: date

    def to_mapping(self, date_format: str) -> dict[str, str]:
        return {
            PH_DATE_TODAY: self.date_today.strftime(date_format),
            PH_PROJECT_NO: self.project_number,
            PH_RECEIPT_NO: self.receipt_number or "",
            PH_DOCTYPE: self.doctype,
            PH_HEADER: self.header,
        }


@dataclass(frozen=True)
class DocxDeliveryDate:
    value: date

    def to_mapping(self, date_format: str) -> dict[str, str]:
        return {
            PH_DELIVERY_DATE: self.value.strftime(date_format),
        }
