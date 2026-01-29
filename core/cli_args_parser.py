"""
CLI Argument parsing and validation for heinrich-metallbau CLI.
"""

import argparse
from typing import Iterable

from .input_args import InputArgs, create_liefer_args, create_rechnung_args


def parse_cli_args(argv: Iterable[str] | None = None) -> InputArgs:
    parser = argparse.ArgumentParser(
        description="Generate documents from CSV and Word template."
    )
    parser.add_argument("project_number", type=str, help="4-digit project number")
    parser.add_argument(
        "mode",
        type=str.lower,
        choices=["liefer", "rechnung"],
        help="Mode: liefer or rechnung",
    )
    parser.add_argument(
        "receipt_number",
        type=str,
        nargs="?",
        default=None,
        help="Order number (required for rechnung)",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "liefer" and args.receipt_number:
        parser.error("RECEIPT_NUMBER should not be provided for liefer mode")

    try:
        if args.mode == "liefer":
            return create_liefer_args(args.project_number)
        else:
            return create_rechnung_args(args.project_number, args.receipt_number)
    except ValueError as e:
        parser.error(str(e))
