import streamlit as st
from utils.i18n import t

# Header
st.title(t("home_title"))
st.markdown(t("powered_by"))
st.markdown("<br>", unsafe_allow_html=True)  # Add moderate space between subtitle and content

# Create form for body
with st.form("onboarding", border=False):
    st.write(t("home_intro"))
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(t("your_name"), placeholder="Name")
    with col2:
        surname = st.text_input(t("your_surname"), placeholder="Surname")
    lang = st.selectbox(t("language"), ["English", "Svenska"])
    start = st.form_submit_button(t("start"))

# Logic for button
if start:
    if not name:
        st.warning(t("warn_name_required"))
    else:
        # Save information
        st.session_state.patient_name = name.strip()
        st.session_state.patient_surname = surname.strip()
        st.session_state.language = lang
        st.session_state.chat = []
        st.session_state.tts_played = {}

        # Move to Chat page
        st.switch_page(st.session_state["_page_chat"])
        st.stop()