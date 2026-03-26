"""
heinrich-app CLI utility
"""

import logging
import sys

from src.backend.cli_args_parser import parse_cli_args
from src.backend.config import load_config
from src.backend.csv_loader import load_csv_data
from src.backend.csv_transformer import csv_rows_to_line_items
from src.backend.paths import CONFIG_PATH, get_latest_csv_path, get_project_dir
from src.backend.services import (
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)
    project_dir, _ = get_project_dir(config.data_root, args.project_number)

    if args.mode in ("offer", "delivery"):
        csv_path, _ = get_latest_csv_path(project_dir, config)
        csv_rows = load_csv_data(csv_path, config)
        line_items, _ = csv_rows_to_line_items(csv_rows, config)

        if args.mode == "offer":
            _ = generate_offer(args.project_number, line_items, project_dir, config)
        else:
            _ = generate_delivery(
                args.project_number,
                args.receipt_number,
                line_items,
                project_dir,
                config,
            )
    elif args.mode == "invoice":
        _ = generate_invoice_and_order(
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
