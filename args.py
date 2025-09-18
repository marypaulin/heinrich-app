"""
Argument parsing and validation for heinrich-metallbau CLI.
"""
import argparse
import re
from typing import NamedTuple


class Args(NamedTuple):
    project_number: str
    mode: str
    order_number: str | None

def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Generate documents from CSV and Word template.")
    parser.add_argument('project_number', type=str, help='4-digit project number')
    parser.add_argument('mode', choices=['liefer', 'rechnung'], help='Mode: liefer or rechnung')
    parser.add_argument('order_number', nargs='?', default=None, help='Order number (required for rechnung)')
    args = parser.parse_args()

    if not re.fullmatch(r'\d{4}', args.project_number):
        parser.error('PROJECT_NUMBER must be exactly 4 digits.')
    if args.mode == 'rechnung' and not args.order_number:
        parser.error('ORDER_NUMBER is required for rechnung mode.')
    if args.mode == 'liefer' and args.order_number:
        parser.error('ORDER_NUMBER should not be provided for liefer mode.')
    return Args(
        project_number=args.project_number,
        mode=args.mode,
        order_number=args.order_number
    )
