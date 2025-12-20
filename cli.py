"""
heinrich-metallbau CLI utility
"""
import logging
import sys

from core.cli_args_parser import parse_cli_args
from core.config import load_config
from core.csv_loader import load_csv_data
from core.csv_transformer import csv_rows_to_line_items
from core.paths import CONFIG_PATH, get_latest_csv_path, get_project_dir
from core.services import render_lieferschein, render_rechnung_and_auftrag

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)
    project_dir = get_project_dir(config.data_root, args.project_number)

    if args.mode == 'liefer':
        csv_path = get_latest_csv_path(project_dir)
        csv_rows = load_csv_data(csv_path, config)
        line_items = csv_rows_to_line_items(csv_rows, config)
        render_lieferschein(args.project_number,
                            line_items,
                            project_dir,
                            config)
    elif args.mode == 'rechnung':
        render_rechnung_and_auftrag(
            args.project_number,
            args.receipt_number,
            project_dir,
            config)
    else:
        logging.error(f"Unknown mode: {args.mode}")


if __name__ == '__main__':
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)
        sys.exit(1)
