import streamlit as st
from utils.config import CFG
from utils.state import init_state
from pages import empresa, dashboard, modulo

st.set_page_config(
    page_title="Conciliação Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS
with open("utils/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_state()

# ── ROUTER ──────────────────────────────────────────────────
page = st.session_state.get("page", "empresa")

if page == "empresa":
    empresa.render()
elif page == "dashboard":
    dashboard.render()
elif page == "modulo":
    modulo.render()
