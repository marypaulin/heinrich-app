# pages/2_E-Rechnung.py
import streamlit as st

st.title("E-Rechnung")
st.markdown(
    "Hier entsteht die E-Rechnungs-Funktionalität (zB XRechnung / ZUGFeRD).")

st.subheader("Status")
st.info("Noch nicht implementiert. Diese Seite dient als Platzhalter für die Demo.")

st.subheader("Geplante Schritte")
st.markdown(
    """
- Datenmodell für Rechnungspositionen
- Exportformat auswählen (XRechnung, ZUGFeRD)
- Validierung gegen Schema
- Ausgabe: XML (und optional PDF mit eingebettetem XML)
"""
)

st.divider()
st.button("Dummy: E-Rechnung erzeugen", type="primary")
