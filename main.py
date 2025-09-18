"""
heinrich-metallbau CLI utility
"""
import logging

from args import parse_args
from csv_loader import load_csv_data
from docgen import render_lieferschein, render_pdf_stub
from paths import (find_latest_csv, find_order_folder, get_output_paths,
                   get_template_path)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    args = parse_args()
    order_folder = find_order_folder(args.project_number)
    csv_path = find_latest_csv(order_folder)
    template_path = get_template_path()

    try:
        output_paths = get_output_paths(args.project_number, args.mode, args.order_number)
    except ValueError as e:
        logging.error(str(e))
        return

    if args.mode == 'liefer':
        data = load_csv_data(csv_path)
        # TODO: Transform CSV data as needed for template
        docx_path = output_paths['docx']
        pdf_path = output_paths['pdf']
        render_lieferschein(template_path, data, docx_path)
        render_pdf_stub(pdf_path)
    elif args.mode == 'rechnung':
        logging.info('Rechnung mode is scaffolded only. TODO: Implement ORDER_NUMBER logic and document generation.')
        # Example: output_paths['auftragsbestaetigung_docx'], output_paths['rechnung_docx'], ...
        # TODO: Implement ORDER_NUMBER logic and document generation
    else:
        logging.error(f"Unknown mode: {args.mode}")

if __name__ == '__main__':
    main()
