import streamlit as st

from backend.config import Config, load_config
from backend.paths import CONFIG_PATH


def get_config() -> Config:
    return st.session_state.setdefault("config", load_config(CONFIG_PATH))


def initialize_session_state() -> None:
    # Session state for UI messages
    if "delivery_info" not in st.session_state:
        st.session_state.delivery_info = []
    if "delivery_error" not in st.session_state:
        st.session_state.delivery_error = None
    if "invoice_info" not in st.session_state:
        st.session_state.invoice_info = []
    if "invoice_error" not in st.session_state:
        st.session_state.invoice_error = None
