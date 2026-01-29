import re
from dataclasses import dataclass
from typing import Literal, Union

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class DeliveryArgs:
    project_number: str
    mode: Literal["delivery"]


@dataclass(frozen=True)
class InvoiceArgs:
    project_number: str
    mode: Literal["invoice"]
    receipt_number: str


InputArgs = Union[DeliveryArgs, InvoiceArgs]


def create_delivery_args(project_number: str) -> DeliveryArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    return DeliveryArgs(project_number=project_number, mode="delivery")


def create_invoice_args(project_number: str, receipt_number: str) -> InvoiceArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required for invoice mode")
    return InvoiceArgs(
        project_number=project_number, mode="invoice", receipt_number=receipt_number
    )
