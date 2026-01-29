import re
from dataclasses import dataclass
from typing import Literal, Union

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class LieferArgs:
    project_number: str
    mode: Literal["liefer"]


@dataclass(frozen=True)
class RechnungArgs:
    project_number: str
    mode: Literal["rechnung"]
    receipt_number: str


InputArgs = Union[LieferArgs, RechnungArgs]


def create_liefer_args(project_number: str) -> LieferArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    return LieferArgs(project_number=project_number, mode="liefer")


def create_rechnung_args(project_number: str, receipt_number: str) -> RechnungArgs:
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required for rechnung mode")
    return RechnungArgs(
        project_number=project_number, mode="rechnung", receipt_number=receipt_number
    )
