import streamlit as st

I18N = {
    # --- Home ---
    "home_title": {"English": "Welcome to your AI Medical Assistant", "Svenska": "Välkommen till din AI-vårdassistent"},
    "powered_by": {"English": "(Powered by GPT-5)", "Svenska": "(Drivs av GPT-5)"},
    "home_intro": {
        "English": "Please, introduce your name and select a language to start your session:",
        "Svenska": "Ange ditt namn och välj språk för att starta din session:"
    },
    "your_name": {"English": "Your name", "Svenska": "Ditt namn"},
    "your_surname": {"English": "Your surname", "Svenska": "Ditt efternamn"},
    "full_name_ph": {"English": "Full name", "Svenska": "Fullständigt namn"},
    "language": {"English": "Language", "Svenska": "Språk"},
    "start": {"English": "Start ➡️", "Svenska": "Starta ➡️"},
    "warn_name_required": {
        "English": "Please, introduce your full name to continue.",
        "Svenska": "Ange ditt fullständiga namn för att fortsätta."
    },

    # --- Chat (headers / inputs) ---
    "chat_title": {"English": "Welcome to your AI Medical Assistant", "Svenska": "Välkommen till din AI-vårdassistent"},
    "write_message_ph": {"English": "Write your message...", "Svenska": "Skriv ditt meddelande..."},
    "spinner_thinking": {"English": "Thinking...", "Svenska": "Tänker..."},
    "spinner_tts": {"English": "Generating voice message...", "Svenska": "Skapar röstmeddelande..."},

    # --- Welcome messages ---
    "welcome_msg": {
        "English": (
            "Hello {name}, I am your consent assistant.\n\n"
            "1) Tell me what procedure you are going to have done (e.g., *‘mole removal’*). "
            "I will generate a clear **consent summary**.\n"
            "2) Then you can ask questions such as *‘Will it hurt?’* or *‘How long does recovery take?’*\n"
            "3) Once you are satisfied, we will save your **informed consent**\n"
            "   - By means of your signature or name.\n"
            "   - By saying aloud into the microphone 'I have read the information and I'm confident about the procedure'.\n"
        ),
        "Svenska": (
            "Hej {name}, jag är din samtyckesassistent.\n\n"
            "1) Berätta vilket ingrepp du ska göra (t.ex. *‘borttagning av födelsemärke’*). "
            "Jag skapar en tydlig **samtyckessammanfattning**.\n"
            "2) Sedan kan du ställa frågor, t.ex. *‘Gör det ont?’* eller *‘Hur lång är återhämtningen?’*\n"
            "3) När du känner dig trygg sparar vi ditt **informerade samtycke**."
            "   - Genom din underskrift eller ditt namn."
            "   - Genom att säga högt i mikrofonen: 'Jag har läst informationen och känner mig trygg med ingreppet'."
        ),
    },

    # --- Consent summary ---.
    "procedure_label": {"English": "Procedure", "Svenska": "Ingrepp"},
    "procedure_not_found": {"English": "Procedure not found", "Svenska": "Procedur hittades inte"},
    "title": {"English": "Title", "Svenska": "Titel"},
    "benefits": {"English": "Benefits", "Svenska": "Fördelar"},
    "benefits_not_found": {"English": "'Benefits' section not found", "Svenska": "Avsnittet 'Fördelar' hittades inte"},
    "alternatives": {"English": "Alternatives", "Svenska": "Alternativ"},
    "alternatives_not_found": {"English": "'Alternatives' section not found", "Svenska": "Avsnittet 'Alternativ' hittades inte"},
    "common_risks": {"English": "Common Risks", "Svenska": "Vanliga risker"},
    "common_risks_not_found": {"English": "'Common risks' section not found", "Svenska": "Avsnittet 'Vanliga risker' hittades inte"},
    "rare_risks": {"English": "Rare Risks", "Svenska": "Sällsynta risker"},
    "rare_risks_not_found": {"English": "'Rare risks' section not found", "Svenska": "Avsnittet 'Sällsynta risker' hittades inte"},
    "preparation": {"English": "Preparation", "Svenska": "Förberedelser"},
    "preparation_not_found": {"English": "'Preparation' section not found", "Svenska": "Avsnittet 'Förberedelser' hittades inte"},
    "seek_help": {"English": "When to seek help", "Svenska": "När du ska söka vård"},
    "seek_help_not_found": {"English": "'When to seek help' section not found", "Svenska": "Avsnittet 'När ska man söka hjälp' hittades inte"},
    "overview": {"English": "Overview", "Svenska": "Översikt"},
    "overview_not_found": {"English": "Overview not found", "Svenska": "Översikt hittades inte"},
    "more_questions": {"English": "More questions or click 'Save consent' button", "Svenska": "Fler frågor eller klicka på knappen 'Spara samtycke'"},

    # --- Consent / signature ---
    "consent_checkbox": {
        "English": "I have read the information and I'm confident about the procedure.",
        "Svenska": "Jag har läst informationen och känner mig trygg med ingreppet."
    },
    "consent_saved": {"English": "Consent registered. Thank you.", "Svenska": "Samtycke registrerat. Tack."},
    "consent_failed": {
        "English": "Something failed. Please, try later or call the medical team reporting the error.",
        "Svenska": "Något gick fel. Försök igen senare eller kontakta vårdteamet och rapportera felet."
    },
    "sign_alt_label": {
        "English": "Otherwise, you can simply write your full name below:",
        "Svenska": "Du kan annars skriva ditt fullständiga namn nedan:"
    },
    "save_consent": {"English": "Save consent", "Svenska": "Spara samtycke"},
    "warn_type_name": {"English": "Please, insert your full name above.", "Svenska": "Ange ditt fullständiga namn ovan."},

    # --- Errors ---
    "error_generic": {"English": "Error: {error}. Please, try later again.", "Svenska": "Fel: {error}. Försök igen senare."},
    "error_transcription": {"English": "Transcription failed", "Svenska": "Transkriptionen misslyckades"},
}

def t(key: str, **fmt) -> str:
    lang = st.session_state.get("language", "English")
    txt = I18N.get(key, {}).get(lang) or I18N.get(key, {}).get("English") or key
    return txt.format(**fmt) if fmt else txt
