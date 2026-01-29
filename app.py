import streamlit as st

from core.csv_loader import load_csv_data
from core.csv_transformer import csv_rows_to_line_items
from core.input_args import create_delivery_args, create_invoice_args
from core.paths import get_latest_csv_path, get_project_dir
from core.services import (
    generate_delivery_note,
    generate_invoice_and_order_confirmation,
)
from state import get_config, initialize_session_state

st.set_page_config(
    page_title="Heinrich App",
    page_icon="assets/icon.ico",
    layout="centered",
)


def suppress_round_corners():
    st.markdown(
        """
        <style>
        img {
            border-radius: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_delivery(config):
    # Reset log messages each time
    st.session_state.delivery_info = []
    st.session_state.delivery_error = None

    project_number_delivery = st.session_state.get(
        "project_number_delivery", ""
    ).strip()

    # Catch error if button is clicked without project number
    if not project_number_delivery:
        st.session_state.delivery_info.append("Bitte eine Projektnummer eingeben.")
        return

    try:
        # Find project dir, read csv, and generate delivery note
        # Log messages from backend for each step
        args = create_delivery_args(project_number_delivery)
        project_dir, messages = get_project_dir(config.data_root, args.project_number)
        st.session_state.delivery_info.extend(messages)
        csv_path, messages = get_latest_csv_path(project_dir, config)
        st.session_state.delivery_info.extend(messages)
        csv_rows = load_csv_data(csv_path, config)
        line_items, messages = csv_rows_to_line_items(csv_rows, config)
        st.session_state.delivery_info.extend(messages)
        messages = generate_delivery_note(
            args.project_number,
            line_items,
            project_dir,
            config,
        )
        st.session_state.delivery_info.extend(messages)
        st.toast("Lieferschein erzeugt", icon="✅")

    except Exception as e:
        st.session_state.delivery_error = f"Error: {str(e)}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_invoice(config):
    # Reset log messages each time
    st.session_state.invoice_info = []
    st.session_state.invoice_error = []

    project_number_invoice = st.session_state.get("project_number_invoice", "").strip()
    receipt_number = st.session_state.get("receipt_number", "").strip()

    # Catch error if button is clicked without numbers
    if not project_number_invoice or not receipt_number:
        st.session_state.delivery_info.append(
            "Bitte Projekt- und Belegnummer eingeben."
        )
        return

    try:
        # Find project dir and generate invoice and order confirmation
        # Log messages from backend for each step
        args = create_invoice_args(project_number_invoice, receipt_number)
        project_dir, messages = get_project_dir(
            config.data_root,
            args.project_number,
        )
        st.session_state.invoice_info.extend(messages)
        messages = generate_invoice_and_order_confirmation(
            args.project_number,
            args.receipt_number,
            project_dir,
            config,
        )
        st.session_state.invoice_info.extend(messages)
        st.toast("Rechnung und Auftragsbestätigung erzeugt", icon="✅")

    except Exception as e:
        st.session_state.invoice_error = f"Error: {str(e)}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def app():
    suppress_round_corners()
    config = get_config()
    initialize_session_state()

    # Logo
    col1, _, col2 = st.columns(3)
    with col2:
        st.image("assets/logo.png")

    # Title
    st.title("Heinrich App")

    st.markdown(
        "Erstelle **Lieferscheine**, **Auftragsbestätigungen** und "
        "**Rechnungen** direkt aus deinen Zeiterfassungsdaten - "
        "sauber formatiert, mit nur wenigen Klicks 📄"
    )

    # Lieferschein
    st.subheader("Lieferschein")

    with st.form("delivery_form"):
        col1, _ = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_delivery",
                placeholder="zB 1235",
            )

        st.form_submit_button(
            "Lieferschein erzeugen",
            on_click=run_delivery,
            args=(config,),
        )

        # Display log messages under submit button
        if st.session_state.delivery_info:
            st.code(
                "\n".join(st.session_state.delivery_info),
                language="text",
            )

        if st.session_state.delivery_error:
            st.error(st.session_state.delivery_error)

    # Rechnung / Auftragsbestätigung
    st.subheader("Rechnung / Auftragsbestätigung")

    with st.form("invoice_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_invoice",
                placeholder="zB 1235",
            )

        with col2:
            st.text_input(
                "Bitte Belegnummer eingeben",
                key="receipt_number",
                placeholder="zB 4504049161",
            )

        st.form_submit_button(
            "Rechnung und Auftragsbestätigung erzeugen",
            on_click=run_invoice,
            args=(config,),
        )

        # Display log messages under submit button
        if st.session_state.invoice_info:
            st.code(
                "\n".join(st.session_state.invoice_info),
                language="text",
            )

        if st.session_state.invoice_error:
            st.error(st.session_state.invoice_error)


if __name__ == "__main__":
    app()
