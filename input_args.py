import re
from dataclasses import dataclass

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class InputArgs:
    project_number: str
    mode: str
    receipt_number: str | None


def create_liefer_args(project_number: str) -> InputArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    return InputArgs(
        project_number=project_number,
        mode="liefer",
        receipt_number=None
    )


def create_rechnung_args(project_number: str, receipt_number: str) -> InputArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required for rechnung mode")
    return InputArgs(
        project_number=project_number,
        mode="rechnung",
        receipt_number=receipt_number
    )
