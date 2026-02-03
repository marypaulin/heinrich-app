"""
CLI Argument parsing and validation for heinrich-metallbau CLI.
"""

import argparse
from typing import Iterable

from .input_args import InputArgs, create_delivery_args, create_invoice_args


def parse_cli_args(argv: Iterable[str] | None = None) -> InputArgs:
    parser = argparse.ArgumentParser(
        description="Generate documents from CSV and Word template."
    )
    parser.add_argument("project_number", type=str, help="4-digit project number")
    parser.add_argument(
        "mode",
        type=str.lower,
        choices=["delivery", "invoice"],
        help="Mode: delivery or invoice",
    )
    parser.add_argument(
        "receipt_number",
        type=str,
        nargs="?",
        default=None,
        help="Receipt number (required for invoice)",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "delivery" and args.receipt_number:
        parser.error("RECEIPT_NUMBER should not be provided for delivery mode")

    try:
        if args.mode == "delivery":
            return create_delivery_args(args.project_number)
        else:
            return create_invoice_args(args.project_number, args.receipt_number)
    except ValueError as e:
        parser.error(str(e))
