"""
heinrich-metallbau CLI utility
"""
import logging
import sys

from cli_args_parser import parse_cli_args
from core.config import load_config
from csv_loader import load_csv_data
from docgen import render_lieferschein, render_rechnung_and_auftrag
from paths import CONFIG_PATH, get_latest_csv_path, get_project_dir

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)
    project_dir = get_project_dir(config.data_root, args.project_number)

    if args.mode == 'liefer':
        csv_path = get_latest_csv_path(project_dir)
        data = load_csv_data(csv_path)
        try:
            render_lieferschein(args.project_number,
                                data,
                                project_dir)
        except ValueError as e:
            logging.error(str(e))
            sys.exit(1)
    elif args.mode == 'rechnung':
        try:
            render_rechnung_and_auftrag(
                args.project_number,
                args.receipt_number,
                project_dir)
        except ValueError as e:
            logging.error(str(e))
            sys.exit(1)
    else:
        logging.error(f"Unknown mode: {args.mode}")


if __name__ == '__main__':
    main()
