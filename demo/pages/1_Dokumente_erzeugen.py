# pages/1_Dokumente_erzeugen.py
import streamlit as st


def init_state():
    st.session_state.setdefault("liefer_info", [])
    st.session_state.setdefault("liefer_error", None)

    st.session_state.setdefault("rechnung_info", [])
    st.session_state.setdefault("rechnung_error", None)


def run_lieferschein():
    st.session_state.liefer_info = []
    st.session_state.liefer_error = None

    project_number = st.session_state.get("project_number_liefer", "").strip()

    if not project_number:
        st.session_state.liefer_info.append(
            "Bitte Projektnummer eingeben (zB 1235).")
        return

    try:
        st.session_state.liefer_info.append("Starte Lieferscheinerstellung")
        st.session_state.liefer_info.append(
            f"Projekt gewählt: {project_number}")
        st.session_state.liefer_info.append(
            "Projektordner gefunden: 1235 - Allgemein Juli")
        st.session_state.liefer_info.append(
            "CSV Datei gefunden: heinrich_zeiterfassung_2025-08-01.csv")
        st.session_state.liefer_info.append(
            "Achtung: Zeile 2 übersprungen wegen ungültiger Auftragsnummer 123")
        st.session_state.liefer_info.append("Template geladen: Vordruck.docx")
        st.session_state.liefer_info.append(
            "DOCX erzeugt: Lieferschein Nr. 1235.docx")
        st.session_state.liefer_info.append(
            "PDF erzeugt: Lieferschein Nr. 1235.pdf")

        st.toast("Lieferschein erzeugt", icon="✅")

    except Exception as e:
        st.session_state.liefer_error = str(e)
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_rechnung():
    st.session_state.rechnung_info = []
    st.session_state.rechnung_error = None

    project_number = st.session_state.get(
        "project_number_rechnung", "").strip()
    receipt_number = st.session_state.get("receipt_number", "").strip()

    if not project_number or not receipt_number:
        st.session_state.rechnung_info.append(
            "Bitte Projektnummer und Belegnummer eingeben.")
        return

    try:
        st.session_state.rechnung_info.append(
            "Starte Rechnung/Auftragsbestätigung")
        st.session_state.rechnung_info.append(f"Projekt: {project_number}")
        st.session_state.rechnung_info.append(f"Belegnummer: {receipt_number}")
        st.session_state.rechnung_info.append("Projektordner gefunden")
        st.session_state.rechnung_info.append("DOCX erzeugt: Rechnung.docx")
        st.session_state.rechnung_info.append(
            "DOCX erzeugt: Auftragsbestätigung.docx")
        st.session_state.rechnung_info.append("PDF erzeugt: Rechnung.pdf")
        st.session_state.rechnung_info.append(
            "PDF erzeugt: Auftragsbestätigung.pdf")

        st.toast("Rechnung und Auftragsbestätigung erzeugt", icon="✅")

    except Exception as e:
        st.session_state.rechnung_error = str(e)
        st.toast("Fehler beim Erzeugen", icon="❌")


init_state()

st.title("Dokumente erzeugen")
st.markdown(
    "Erstelle Lieferscheine, Auftragsbestätigungen und Rechnungen aus deinen Projektdaten.")

st.subheader("Lieferschein")

with st.form("lieferschein_form"):
    col1, _ = st.columns(2)
    with col1:
        st.text_input(
            "Bitte Projektnummer eingeben",
            key="project_number_liefer",
            placeholder="zB 1235",
        )

    st.form_submit_button("Lieferschein erzeugen", on_click=run_lieferschein)

    if st.session_state.liefer_error:
        st.error(st.session_state.liefer_error)

    if st.session_state.liefer_info:
        st.code("\n".join(st.session_state.liefer_info), language="text")

st.divider()

st.subheader("Rechnung / Auftragsbestätigung")

with st.form("rechnung_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Bitte Projektnummer eingeben",
            key="project_number_rechnung",
            placeholder="zB 1235",
        )
    with col2:
        st.text_input(
            "Bitte Belegnummer eingeben",
            key="receipt_number",
            placeholder="zB 17887857",
        )

    st.form_submit_button(
        "Rechnung und Auftragsbestätigung erzeugen", on_click=run_rechnung)

    if st.session_state.rechnung_error:
        st.error(st.session_state.rechnung_error)

    if st.session_state.rechnung_info:
        st.code("\n".join(st.session_state.rechnung_info), language="text")
