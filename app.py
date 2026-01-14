import streamlit as st

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

col1, _, col2 = st.columns(3)
with col2:
    st.image("logo.png")

st.title("Heinrich App")

st.markdown("Erstelle **Lieferscheine**, **Auftragsbestätigungen** und "
            "**Rechnungen** direkt aus deinen Zeiterfassungsdaten"
            "- sauber formatiert und mit nur wenigen Klicks 📄")

# ---------------- Lieferschein ----------------
st.subheader("Lieferschein")

with st.form("lieferschein_form"):
    col1, _ = st.columns(2)

    with col1:
        project_number_ls = st.text_input(
            "Bitte Projektnummer eingeben"
        )
    submit_ls = st.form_submit_button("Lieferschein erzeugen")

if submit_ls:
    st.write(f"Sie haben gewählt: {project_number_ls}")

# ---------------- Rechnung / Auftragsbestätigung ----------------
st.subheader("Rechnung / Auftragsbestätigung")

with st.form("rechnung_form"):
    col1, col2 = st.columns(2)

    with col1:
        project_number_re = st.text_input(
            "Bitte Projektnummer eingeben"
        )

    with col2:
        receipt_number = st.text_input(
            "Bitte Belegnummer eingeben"
        )

    submit_re = st.form_submit_button(
        "Rechnung und Auftragsbestätigung erzeugen"
    )

if submit_re:
    st.write(
        f"Sie haben gewählt: {project_number_re} und {receipt_number}"
    )
