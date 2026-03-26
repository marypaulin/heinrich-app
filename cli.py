"""
heinrich-app CLI utility
"""

import logging
import sys

from src.backend.cli_args_parser import parse_cli_args
from src.backend.config import load_config
from src.backend.paths import CONFIG_PATH
from src.backend.services import (
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)

    if args.mode == "offer":
        generate_offer(args.project_number, config)
    elif args.mode == "delivery":
        generate_delivery(args.project_number, args.receipt_number, config)
    elif args.mode == "invoice":
        generate_invoice_and_order(args.project_number, args.receipt_number, config)
    else:
        logging.error(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)
        sys.exit(1)
