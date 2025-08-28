import streamlit as st
from pathlib import Path
import requests
from uuid import uuid4

# Import functions
from utils.ui_helpers import check_backend
from utils.config import get_config, get_custom_css

# Setup the page configuration.
config = get_config()
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE
)

# Apply custom CSS to the application.
st.markdown(get_custom_css(), unsafe_allow_html=True)


# Initialize session state variables
ss = st.session_state
ss.setdefault("http", requests.Session())
ss.setdefault("session_id", str(uuid4()))
ss.setdefault("patient_name", "")
ss.setdefault("patient_surname", "")
ss.setdefault("language", "English")
ss.setdefault("chat", [])
ss.setdefault("pending_request", None)
ss.setdefault("agree_consent", False)
ss.setdefault("tts_played", {})

# Check backend
check_backend()

# Define absolute paths
APP_DIR = Path(__file__).resolve().parent          # ← carpeta /app
HOME_PATH = (APP_DIR / "views" / "Home.py").resolve()
CHAT_PATH = (APP_DIR / "views" / "Chat.py").resolve()

# Define pages
home = st.Page(HOME_PATH, title="Home", icon="🏠", url_path="home", default=True)
chat = st.Page(CHAT_PATH, title="Chat", icon="💬", url_path="chat")

# Save references for pages
ss["_page_home"] = home
ss["_page_chat"] = chat

# Define router for navigation in pages
pg = st.navigation([home, chat], position="hidden")
pg.run()
