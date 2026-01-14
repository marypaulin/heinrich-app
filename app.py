import streamlit as st

from core.config import load_config
from core.csv_loader import load_csv_data
from core.csv_transformer import csv_rows_to_line_items
from core.input_args import create_liefer_args, create_rechnung_args
from core.paths import CONFIG_PATH, get_latest_csv_path, get_project_dir
from core.services import render_lieferschein, render_rechnung_and_auftrag


def suppress_round_corners():
    st.markdown(
        """
        <style>
        img {
            border-radius: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_data
def get_config():
    return load_config(CONFIG_PATH)


def app():
    suppress_round_corners()
    config = get_config()

    # TODO Modularisierung + Logging/Feedback

    # Logo
    col1, _, col2 = st.columns(3)
    with col2:
        st.image("assets/logo.png")

    # Title
    st.title("Heinrich App")

    st.markdown("Erstelle **Lieferscheine**, **Auftragsbestätigungen** und "
                "**Rechnungen** direkt aus deinen Zeiterfassungsdaten - "
                "sauber formatiert, mit nur wenigen Klicks 📄")

    # Lieferschein
    st.subheader("Lieferschein")

    with st.form("lieferschein_form"):
        col1, _ = st.columns(2)

        with col1:
            project_number_liefer = st.text_input(
                "Bitte Projektnummer eingeben"
            )
        submit_liefer = st.form_submit_button("Lieferschein erzeugen")

    if submit_liefer:
        st.write(f"Sie haben gewählt: {project_number_liefer}")
        args = create_liefer_args(project_number_liefer)
        project_dir = get_project_dir(config.data_root, args.project_number)
        csv_path = get_latest_csv_path(project_dir, config)
        csv_rows = load_csv_data(csv_path, config)
        line_items = csv_rows_to_line_items(csv_rows, config)
        render_lieferschein(args.project_number,
                            line_items,
                            project_dir,
                            config)

    # Rechnung / Auftragsbestätigung
    st.subheader("Rechnung / Auftragsbestätigung")

    with st.form("rechnung_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_number_rechnung = st.text_input(
                "Bitte Projektnummer eingeben"
            )

        with col2:
            receipt_number = st.text_input(
                "Bitte Belegnummer eingeben"
            )

        submit_rechnung = st.form_submit_button(
            "Rechnung und Auftragsbestätigung erzeugen"
        )

    if submit_rechnung:
        st.write(
            f"Sie haben gewählt: {project_number_rechnung} und {receipt_number}"
        )
        args = create_rechnung_args(project_number_rechnung, receipt_number)
        project_dir = get_project_dir(config.data_root, args.project_number)
        render_rechnung_and_auftrag(
            args.project_number,
            args.receipt_number,
            project_dir,
            config)


if __name__ == "__main__":
    app()
