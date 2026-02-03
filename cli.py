"""
heinrich-app CLI utility
"""

import logging
import sys

from backend.cli_args_parser import parse_cli_args
from backend.config import load_config
from backend.csv_loader import load_csv_data
from backend.csv_transformer import csv_rows_to_line_items
from backend.paths import CONFIG_PATH, get_latest_csv_path, get_project_dir
from backend.services import (
    generate_delivery_note,
    generate_invoice_and_order_confirmation,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)
    project_dir, _ = get_project_dir(config.data_root, args.project_number)

    if args.mode == "delivery":
        csv_path, _ = get_latest_csv_path(project_dir, config)
        csv_rows = load_csv_data(csv_path, config)
        line_items, _ = csv_rows_to_line_items(csv_rows, config)
        _ = generate_delivery_note(args.project_number, line_items, project_dir, config)
    elif args.mode == "invoice":
        _ = generate_invoice_and_order_confirmation(
            args.project_number, args.receipt_number, project_dir, config
        )
    else:
        logging.error(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)
        sys.exit(1)
