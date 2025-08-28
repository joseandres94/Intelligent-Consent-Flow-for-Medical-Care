import os
import sys
import datetime
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Add the project root to the Python path for proper imports
#current_dir = os.path.dirname(os.path.abspath(__file__))
#project_root = os.path.dirname(current_dir)
#if project_root not in sys.path:
#    sys.path.insert(0, project_root)

# Import functions
from utils.ui_helpers import api_post
from utils.i18n import t

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


# Functions definition
def process_text(text_input: str, type: str):
    """
    Function that handles API call for text generation by LLM.
    """

    try:
        # Call API
        payload = {
            "session_id": st.session_state.session_id,
            "text_input": text_input,
            "stage": "",
            "language": st.session_state.language
        }
        response = api_post("/chat", json=payload)
        response.raise_for_status()

        # Extract response
        data = response.json()
        answer = data.get("answer", "").strip()
        summary = data.get("summary")
        stage = data.get("stage")

        if stage == "summary":
            assistant_message = summary
        else:
            assistant_message = f"""
                {answer}"""

        # Append message to chat
        st.session_state.chat.append({"id": str(uuid4()),
                                      "role": "assistant",
                                      "type": type,
                                      "content": assistant_message,
                                      "stage": stage})

    except Exception as e:
        assistant_message = t("error_generic").format(error=e)
        st.session_state.chat.append({"id": str(uuid4()), "role": "assistant", "type": "text",
                                      "content": assistant_message, "stage": "error"})


def process_audio(audio_input) -> str:
    """
    Function that handles API call for Speech-to-Text generation.
    """

    # Extract content from audio
    blob = audio_input.getvalue()
    fname = getattr(audio_input, "name", "recording.wav")
    mime = getattr(audio_input, "type", "audio/wav")

    # Avoid processing same audio
    sig = (len(blob), fname)
    if st.session_state.get("last_audio_sig") != sig or not st.session_state.get("last_audio_sig"):
        st.session_state["last_audio_sig"] = sig
        try:
            # Call API
            files = {
                "file": (fname, blob, mime),
            }
            data = {
                "session_id": st.session_state.session_id,
                "language": st.session_state.language,  # "English" | "Svenska"
            }
            r = st.session_state.http.post(
                f"{BACKEND_URL}/transcribe",
                data=data,
                files=files,
                timeout=60
            )
            r.raise_for_status()

            # Extract response
            tx = (r.json()).strip()

        except Exception as e:
            tx = ""
            st.error(t("error_transcription") + f": {e}")

        if tx:
            return tx


def generate_tts(session_id: str, text_input: str, stage: str, language: str) -> bytes:
    """
    Function that handles API call for Text-to-Speech generation.
    """

    # Call API
    payload = {
        "session_id": session_id,
        "text_input": text_input,
        "stage": stage,
        "language": language
    }
    r = api_post("/tts", json=payload)
    r.raise_for_status()

    # Return response content
    return r.content  # Audio bytes


def create_signature_space(id: str) -> bool:
    """
    Function that builds signature section.
    """

    # Define drawing mode
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("freedraw", "line", "rect", "transform")
    )

    # Create a canvas component for signature
    canvas_result = st_canvas(
        stroke_width=5,
        background_color="#eee",
        height=150,
        drawing_mode=drawing_mode,
        key=f"canvas_{id}",
        display_toolbar=True
    )

    # Create a text box for signature
    signature_name = st.text_input(t("sign_alt_label"),
                                   key=f"textbox_{id}",
                                   placeholder=t("full_name_ph"),
                                   width=600)

    # Create a button for consent registration
    clicked_consent = st.button(
        t("save_consent"),
        key=f"button_consent_{id}"
    )

    # Consent agreement (if button clicked)
    if clicked_consent:
        method = ""
        if signature_name or canvas_result:
            if signature_name:
                method = "typed"
            if canvas_result:
                method = "signature"
            if signature_name and canvas_result:
                method = "typed+signature"

            # Call API
            payload = {
                "patient_name": signature_name or st.session_state.patient_name,
                "session_id": st.session_state.session_id,
                "method": method,
                "timestamp": str(datetime.datetime.now().timestamp())
            }
            response = api_post("/consent", json=payload)
            response.raise_for_status()

            # Return result
            if response.json().get("ok") == True:
                st.success(t("consent_saved"))
                return True
            else:
                st.error(t("consent_failed"))
                return False

        else:
            st.warning(t("warn_type_name"))
            return False
    else:
        return False


def render_consent_summary(sections: dict):
    """
    Function that renders consent summary.
    """

    def _md_list(value):
        if isinstance(value, list):
            return "\n".join(f"- {item}" for item in value) if value else ""
        return str(value).strip()

    # Main space
    with st.container(border=False):
        st.markdown(f"#### {t('procedure_label')}: {sections.get(t('title'), t('procedure_not_found'))}")#####
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(_md_list(sections.get(t('overview'), t("procedure_not_found"))))
        st.markdown("<br>", unsafe_allow_html=True)

        # Two columns to make it more compact
        col1, col2 = st.columns(2, vertical_alignment="top")
        with col1:
            st.markdown(f"**✅ {t('benefits')}**")
            st.markdown(_md_list(sections.get(t('benefits'), t("benefits_not_found"))))

        with col2:
            st.markdown(f"**🔄 {t('alternatives')}**")
            st.markdown(_md_list(sections.get(t('alternatives'), t("alternatives_not_found"))))

        st.markdown("<br>", unsafe_allow_html=True)

        # Two columns to make it more compact
        col1, col2 = st.columns(2, vertical_alignment="top")
        with col1:
            st.markdown(f"**⚠️ {t('common_risks')}**")
            st.markdown(_md_list(sections.get(t('common_risks'), t("common_risks_not_found"))))

        with col2:
            st.markdown(f"**❗ {t('rare_risks')}**")
            st.markdown(_md_list(sections.get(t('rare_risks'), t("rare_risks_not_found"))))

        st.markdown("<br>", unsafe_allow_html=True)

        # Two columns to make it more compact
        col1, col2 = st.columns(2, vertical_alignment="top")
        with col1:
            st.markdown(f"**🧰 {t('preparation')}**")
            st.markdown(_md_list(sections.get(t('preparation'), t("preparation_not_found"))))

        with col2:
            st.markdown(f"**🚑 {t('seek_help')}**")
            st.markdown(_md_list(sections.get(t('seek_help'), t("seek_help_not_found"))))

        # Last paragraph
        if sections.get(f"{t('more_questions')}"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(sections.get(f"{t('more_questions')}", ""))
        st.markdown("<br>", unsafe_allow_html=True)

# Header
st.title(t("home_title"))
st.markdown(t("powered_by"))
st.markdown("<br>", unsafe_allow_html=True)  # Add moderate space between subtitle and content

# Create sidebar
with st.sidebar:
    # Display Session Id
    st.caption(f"Session ID: {st.session_state.session_id}")

    # Create 'Home' button
    if st.button("Go home"):
        st.switch_page(st.session_state["_page_home"])

    # Restart conversation
    if st.button("Restart conversation"):
        st.session_state.chat = st.session_state.chat[:1]
        st.session_state.last_summary = ""

# Main body
if not st.session_state.chat:  # Injects welcome message if empty
    lang = st.session_state.get("language", "English")
    name = st.session_state.get("patient_name", "").strip() or "patient"
    st.session_state.chat = [{
        "id": str(uuid4()),
        "role": "assistant",
        "type": "text",
        "content": t("welcome_msg").format(name=name),
        "stage": "welcome"
    }]

# Get pending requests
pending = st.session_state.get("pending_request")

with (st.container(border=False, height=450)):
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            # Display text messages
            if msg["role"] == "assistant" and msg["stage"] == "summary":
                render_consent_summary(msg["content"])
            else:
                st.write(msg["content"])
                st.markdown("<br>", unsafe_allow_html=True)

            # Display voice audio from AI response
            if msg["role"] == "assistant" and msg["type"] == "audio":
                if msg["id"] not in st.session_state.tts_played:
                    with st.spinner("🎙️" + t("spinner_tts")):
                        audio_bytes = generate_tts(session_id = msg["id"],
                                                   text_input = str(msg["content"]),
                                                   stage = msg["stage"],
                                                   language = st.session_state.language)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.audio(audio_bytes, format="audio/wav", autoplay=True)
                    st.session_state.tts_played[msg["id"]] = audio_bytes

                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.audio(st.session_state.tts_played[msg["id"]], format="audio/wav", autoplay=False)

            # Consent checkbox
            if (msg["role"] == "assistant" and msg["stage"] == "summary" or msg["stage"] == "qa") \
                and not st.session_state.agree_consent:
                agree = st.checkbox(t("consent_checkbox"),
                                    key=f"check_{msg['id']}")
                if agree:
                    st.session_state.agree_consent = create_signature_space(msg["id"])

            elif (msg["role"] == "assistant" and msg["stage"] == "summary" or msg["stage"] == "qa") and st.session_state.agree_consent:
                st.success(t("consent_saved"))

        # Display spinner
        if pending and msg["role"] == "user" and msg.get("id") == pending.get("message_id"):
            with st.spinner("🤔🧠 " + t("spinner_thinking")):
                process_text(pending["text"], type=pending["type"])
                st.session_state["pending_request"] = None
                st.rerun()

# Input section
col1, col2 = st.columns([0.75, 0.25])
with col1:
    text_input = st.chat_input(t("write_message_ph"))
    if text_input:
        msg_id = str(uuid4())
        st.session_state.chat.append({"id": msg_id, "role": "user", "type": "text", "content": text_input,
                                      "stage": "input"})
        st.session_state["pending_request"] = {"message_id": msg_id, "type": "text", "text": text_input}
        st.rerun()

with col2:
    audio_input = st.audio_input("Record", key="voice_mic", label_visibility="collapsed")
    if audio_input:
        msg_id = str(uuid4())
        transcription = process_audio(audio_input)
        if transcription:
            # Check if consent recorded
            if transcription == t("consent_checkbox") and st.session_state.chat:
                # Call API
                payload = {
                    "patient_name": st.session_state.patient_name,
                    "session_id": st.session_state.session_id,
                    "method": "voice",
                    "timestamp": str(datetime.datetime.now().timestamp())
                }
                response = api_post("/consent", json=payload)
                response.raise_for_status()

                # Display result
                if response.json().get("ok") == True:
                    st.success(t("consent_saved"))
                else:
                    st.error(t("consent_failed"))

            # Process message transcripted
            else:
                st.session_state.chat.append({"id": msg_id, "role": "user", "type": "audio", "content": transcription,
                                              "stage": "input"})
                st.session_state["pending_request"] = {"message_id": msg_id, "type": "audio", "text": transcription}
                st.rerun()