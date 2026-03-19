import streamlit as st
import os
from utils.config import CFG
from utils.state import init_state
from pages import empresa, dashboard, modulo

st.set_page_config(
    page_title="Conciliação Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS — path relative to this file
_here = os.path.dirname(os.path.abspath(__file__))
_css_path = os.path.join(_here, "utils", "style.css")
try:
    with open(_css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass  # CSS optional — app still works without it

init_state()

# ── ROUTER ──────────────────────────────────────────────────
page = st.session_state.get("page", "empresa")

if page == "empresa":
    empresa.render()
elif page == "dashboard":
    dashboard.render()
elif page == "modulo":
    modulo.render()
