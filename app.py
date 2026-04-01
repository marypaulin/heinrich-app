import streamlit as st

from src.backend.services import (
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
)
from src.ui.state import get_config, initialize_session_state

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


def run_offer(config):
    st.session_state.offer_info = []
    st.session_state.offer_error = None

    project_number = st.session_state.get("project_number_offer", "").strip()
    if not project_number:
        st.session_state.offer_info.append("Bitte eine Projektnummer eingeben.")
        return

    try:
        st.session_state.offer_info = generate_offer(project_number, config)
        st.toast("Angebot erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.offer_error = f"Error: {str(e)}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_delivery(config):
    st.session_state.delivery_info = []
    st.session_state.delivery_error = None

    project_number = st.session_state.get("project_number_delivery", "").strip()
    if not project_number:
        st.session_state.delivery_info.append("Bitte eine Projektnummer eingeben.")
        return

    receipt_number = st.session_state.get("receipt_number_delivery", "").strip() or None

    try:
        st.session_state.delivery_info = generate_delivery(
            project_number, receipt_number, config
        )
        st.toast("Lieferschein erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.delivery_error = f"Error: {str(e)}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_invoice(config):
    st.session_state.invoice_info = []
    st.session_state.invoice_error = []

    project_number = st.session_state.get("project_number_invoice", "").strip()
    receipt_number = st.session_state.get("receipt_number_invoice", "").strip()

    if not project_number or not receipt_number:
        st.session_state.invoice_info.append(
            "Bitte Projekt- und Belegnummer eingeben."
        )
        return

    try:
        st.session_state.invoice_info = generate_invoice_and_order(
            project_number, receipt_number, config
        )
        st.toast("Rechnung und Auftragsbestätigung erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
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
    st.title("RHI Abrechnung")

    # Introduction
    st.markdown(
        "Erstelle **Angebote**, **Lieferscheine**, **Rechnungen** und **Auftragsbestätigungen** "
        "für RHI direkt aus deinen Zeiterfassungsdaten.\n"
        "Die Konfiguration erfolgt über die Datei `heinrich-app/config.json`. "
    )

    # Angebot
    st.subheader("Angebot")

    with st.form("offer_form"):
        col1, _ = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_offer",
                placeholder="zB 1235",
            )

        st.form_submit_button(
            "Angebot erzeugen",
            on_click=run_offer,
            args=(config,),
        )

        if st.session_state.offer_info:
            st.code(
                "\n".join(st.session_state.offer_info),
                language="text",
            )

        if st.session_state.offer_error:
            st.error(st.session_state.offer_error)

    # Lieferschein
    st.subheader("Lieferschein")

    with st.form("delivery_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_delivery",
                placeholder="zB 1235",
            )

        with col2:
            st.text_input(
                "Optional Belegnummer eingeben",
                key="receipt_number_delivery",
                placeholder="zB 4504049161",
            )

        st.form_submit_button(
            "Lieferschein erzeugen",
            on_click=run_delivery,
            args=(config,),
        )

        if st.session_state.delivery_info:
            st.code(
                "\n".join(st.session_state.delivery_info),
                language="text",
            )

        if st.session_state.delivery_error:
            st.error(st.session_state.delivery_error)

    # Rechnung / Auftragsbestätigung
    st.subheader("Rechnung & Auftragsbestätigung")

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
                key="receipt_number_invoice",
                placeholder="zB 4504049161",
            )

        st.form_submit_button(
            "Rechnung und Auftragsbestätigung erzeugen",
            on_click=run_invoice,
            args=(config,),
        )

        if st.session_state.invoice_info:
            st.code(
                "\n".join(st.session_state.invoice_info),
                language="text",
            )

        if st.session_state.invoice_error:
            st.error(st.session_state.invoice_error)


if __name__ == "__main__":
    app()
