import re
from dataclasses import dataclass
from typing import Literal, Union

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class OfferArgs:
    project_number: str
    mode: Literal["offer"]


@dataclass(frozen=True)
class DeliveryArgs:
    project_number: str
    mode: Literal["delivery"]


@dataclass(frozen=True)
class InvoiceArgs:
    project_number: str
    mode: Literal["invoice"]
    receipt_number: str


InputArgs = Union[OfferArgs, DeliveryArgs, InvoiceArgs]


def _validate_project_number(project_number: str) -> None:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")


def create_offer_args(project_number: str) -> OfferArgs:
    _validate_project_number(project_number)
    return OfferArgs(project_number=project_number, mode="offer")


def create_delivery_args(project_number: str) -> DeliveryArgs:
    _validate_project_number(project_number)
    return DeliveryArgs(project_number=project_number, mode="delivery")


def create_invoice_args(project_number: str, receipt_number: str) -> InvoiceArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required for invoice mode")
    return InvoiceArgs(
        project_number=project_number, mode="invoice", receipt_number=receipt_number
    )
