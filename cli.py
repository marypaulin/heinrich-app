"""
heinrich-metallbau CLI utility
"""
import logging

from cli_args_parser import parse_cli_args
from core.config import load_config
from csv_loader import load_csv_data
from docgen import render_lieferschein, render_pdf, render_rechnung_and_auftrag
from paths import (CONFIG_PATH, find_latest_csv, find_project_folder,
                   get_target_paths, get_template_path)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)
    project_folder = find_project_folder(config.data_root, args.project_number)
    try:
        target_paths = get_target_paths(
            project_folder,
            args.project_number,
            args.mode,
            args.receipt_number
        )
    except ValueError as e:
        logging.error(str(e))
        return

    if args.mode == 'liefer':
        csv_path = find_latest_csv(project_folder)
        data = load_csv_data(csv_path)
        template_path = get_template_path()
        target_path = target_paths['liefer']
        render_lieferschein(template_path,
                            args.project_number,
                            data,
                            target_path)
        render_pdf(target_path)
    elif args.mode == 'rechnung':
        render_rechnung_and_auftrag(
            args.project_number,
            args.receipt_number,
            target_paths)
        render_pdf(target_paths["rechnung"])
        render_pdf(target_paths["auftrag"])
    else:
        logging.error(f"Unknown mode: {args.mode}")


if __name__ == '__main__':
    main()
