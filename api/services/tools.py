import os
import logging
import re
import openai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define logger
logger = logging.getLogger(__name__)


class AIService:
    """Service for handling AI model interactions"""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-5-2025-08-07")

        if not self.api_key:
            logger.warning("OpenAI API key not found. AI functionality will be limited.")

            # Initialize OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None


    async def check_availability(self) -> str:
        """Check if the AI service is available"""
        if not self.client:
            return "unavailable"

        try:
            # Simple test call to check API availability
            _ = self.client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=[{"role": "user", "content": "Hello"}],
            )
            return "available"

        except Exception as e:
            logger.error(f"AI service check failed: {str(e)}")
            return "error"


    def _parse_summary(self, md: str) -> Dict[str, Any]:
        """Parse the summary from AI service"""

        header_re = re.compile(r'^(#{1,6})\s*(.+?)\s*$')
        sections: Dict[str, Any] = {}
        current: str | None = None
        buf: List[str] = []

        def flush():
            nonlocal buf, current
            if current is None:
                buf = []
                return
            raw = "\n".join(buf).strip()
            if not raw:
                sections[current] = ""
            else:
                bullets = [m.group(1).strip()
                           for m in re.finditer(r'^\s*[-*]\s+(.*\S)\s*$', raw, flags=re.MULTILINE)]
                sections[current] = bullets if bullets else raw
            buf = []

        for line in md.splitlines():
            m = header_re.match(line)
            if m:
                flush()
                current = m.group(2).strip()
            else:
                buf.append(line)

        flush()
        return sections

    def _summary(self, user_query: str, language: str) -> Dict[str, Any]:
        """Generates patient consent summary"""

        # Create prompts
        if language == "English":
            system_prompt = """
            You are an expert and helpful clinical assistant.
            Goals:
            - Always perform a deep understanding to identify the medical procedure from the user’s input.
            - Write a patient-friendly consent summary at A2/B1 reading level.
            - Be neutral, clear, and compassionate.
            - If the procedure cannot be confidently identified, use a generic name (e.g., “Procedure for <procedure 
            given by user>”) and keep guidance general. Do NOT invent specifics.
            - **CRITICAL**: **ALWAYS PROPOSE** that the patient asks more questions if needed, and
            **PROPOSE** clicking **'Save consent'** button if they feel confident with the provided information.
            
            Behaviour:
            1. Greeting-only input (e.g., “Hello”, “Hi”, “Hey”, “Good morning”, “Good evening”):
                - Manage the conversation as a helpful assistant (e.g., Introduce yourself and ask for a medical
                procedure to help the patient, etc.).
                - Do **NOT** produce the consent template.
                - Invite questions.
            2. Procedure given or can be inferred:
                - Output **ONLY** markdown with **EXACTLY** these headings, in this order, with no extra text or code fences 
                (STRICT and **MANDATORY TO WRITE SOMETHING IN EACH OF THEM**):
                    # Title
                    ## Overview
                    ## Benefits
                    ## Common risks
                    ## Rare risks
                    ## Alternatives
                    ## Preparation
                    ## When to seek help
                    ## More questions or click 'Save consent' button
                - **CRITICAL**: Under ‘Title’ you must **ALWAYS** include the proper name of the procedure 
                (e.g., “Laparoscopy”).

            Style:                
            - Use '-' for bullet lists, except in 'Overview' and 'More questions or click Save consent' sections, which 
            must be short paragraphs/lines.
            - Keep lists short and readable (3–6 bullets when possible).
            - No legal or diagnostic claims; this is general information.
            - Write **EVERYTHING** in English.
            
            Few-shot anchors (do not echo triggers back):
            - Input: “Hello” → Friendly intro + ask for procedure; no consent template.
            - Input: “Appendectomy” → Full template with headings above.
            - Input: “Not sure, maybe knee surgery?” → Use generic title: “Procedure for knee surgery (as described by 
            you)” + general guidance.
            """

            user_prompt = f"""
            Patient query:
            {user_query}

            Generate the requested markdown."""

        elif language == "Svenska":
            system_prompt = f"""
            Du är en expert och hjälpsam klinisk assistent.
            Mål:
            - Gör alltid en djupgående analys för att identifiera vilket medicinskt ingrepp användaren beskriver.
            - Skriv en patientvänlig samtyckessammanfattning på läsnivå A2/B1.
            - Var neutral, tydlig och medkännande.
            - Om ingreppet inte kan identifieras med säkerhet, använd ett generiskt namn (t.ex. ”Ingrepp för <ingrepp 
            angivet av användaren>”) och håll vägledningen allmän. Hitta **inte** på detaljer.
            - **KRITISKT**: **FÖRESLÅ ALLTID** att patienten ställer fler frågor vid behov, och **FÖRESLÅ** att klicka
            på knappen **”Spara samtycke”** om patienten känner sig trygg med informationen.
            
            Beteende (strikt ordning och prioritet):
            1. Endast hälsning (t.ex. ”Hej”, ”Hejsan”, ”Hallå”, ”God morgon”, ”God kväll”, ”Tjena”, ”Tja”):
                - Hantera samtalet som en hjälpsam assistent (t.ex. presentera dig själv och fråga om en medicinsk 
                procedur för att hjälpa patienten etc.).
                - Ta **INTE** fram samtyckesmallen.
                - Uppmuntra frågor.
            2. Ingrepp anges eller kan tolkas:
                - Skriv **UTESLUTANDE** markdown med **EXAKT** dessa rubriker, i denna ordning, utan extra text eller kodgränser
                 (STRIKT och **OBLIGATORISKT ATT SKRIVA NÅGOT I VARJE AV DEM**):
                    # Titel
                    ## Översikt
                    ## Fördelar
                    ## Vanliga risker
                    ## Sällsynta risker
                    ## Alternativ
                    ## Förberedelser
                    ## När ska man söka hjälp
                    ## Fler frågor eller klicka på knappen 'Spara samtycke'
            
            - **KRITISKT**: Under ”Titel” måste **ALLTID** ingreppets korrekta namn anges (t.ex. ”Laparoskopi”).

            Stil:
            - Använd '-' för punktlistor, **utom** i avsnitten 'Översikt' och 'Fler frågor eller klicka på Spara 
            samtycke'. 
            Avsnittet 'Översikt' måste vara ett enkelt stycke och 'Fler frågor eller klicka på Spara samtycke' några 
            rader.
            - Håll listorna korta och läsbara (3–6 punkter om möjligt).
            - Inga juridiska eller diagnostiska påståenden; detta är allmän information.
            - Skriv **ALLT på svenska**.
            
            Exempel (ankare – upprepa inte triggarna):
            - Input: ”Hej” → Vänlig presentation + fråga efter ingrepp; ingen samtycksmall.
            - Input: ”Kataraktoperation” → Full mall med rubrikerna ovan.
            - Input: ”Vet inte, något med knät?” → Generisk titel: ”Ingrepp för knä (enligt din beskrivning)” + 
            allmän vägledning.
            """

            user_prompt = f"""
            Patientfråga:
            {user_query}

            Generera den begärda markeringen.
            """

        else:
            system_prompt = ""
            user_prompt = ""


        # Call API
        response = self._call_llm(instructions=system_prompt,
                                  user_input=user_prompt)

        return response

    def _answer_qa(self, question: str, language: str, summary: Dict[str, Any], history: str = ""):
        """Answer questions from patient related to the procedure using the history of the conversation"""

        # Create prompts
        if language == "English":
            system_prompt = """
            You are an expert clinical assistant that answers a patient's questions about an upcoming procedure.
            
            Goals:
            - Answer the question clearly and compassionately at A2/B1 reading level.
            - Stay within the provided consent context; do **NOT** invent facts that are not there.
            - If the question is ambiguous, ask a brief clarifying question.
            - If you are uncertain, say so and suggest speaking with a clinician.
            - If the patient describes urgent red-flag symptoms, advise seeking immediate medical care.
            - **CRITICAL**: **ALWAYS PROPOSE** the patient to make more questions if needed, and **PROPOSE** to click
            **'Save consent'** button if is confident with the provided information about the procedure that is taking.
             
            Style & format:
            - Write EVERYTHING in English.
            - Be concise: 2–6 short sentences, use bullets only if it improves clarity.
            - Do NOT repeat the consent context verbatim; summarize only what’s needed.
            - No legal or diagnostic claims; this is general information.
            You will receive a short conversation recap below; use it only if relevant.
            """

            context =f"""Title: {summary.get('Title', '')}
            Overview: {summary.get('Overview', '')}
            Common risks: {', '.join(summary.get('Common risks', [])[:5])}
            Rare risks: {', '.join(summary.get('Rare risks', [])[:3])}
            Alternatives: {', '.join(summary.get('Alternatives', [])[:3])}
            """

            user_prompt = f"""
            Consent context (do not repeat verbatim):
            {context}
            Short conversation recap:
            {history or '(none)'}
            Patient question:
            {question}
            """

        elif language == "Svenska":
            system_prompt = """
            Du är en klinisk assistent som svarar på en patients frågor om en kommande behandling.
            Mål:
            - Svara på frågan tydligt och med empati på läsnivå A2/B1.
            - Håll dig inom ramen för det angivna samtycket; **INTE** hitta på fakta som inte finns.
            - Om frågan är tvetydig, ställ en kort förtydligande fråga.
            - Om du är osäker, säg det och föreslå att patienten talar med en läkare.
            - Om patienten beskriver akuta varningssymptom, råda patienten att omedelbart söka läkarvård.
            - **VIKTIGT**: **FÖRESLÅ ALLTID** patienten att ställa fler frågor om det behövs, och **FÖRESLÅ** att klicka
            på knappen **”Spara samtycke”** om patienten är nöjd med den information som lämnats om ingreppet.
            
            Stil och format:
            - Skriv ALLT på svenska.
            - Var kortfattad: 2–6 korta meningar, använd punktlistor endast om det förbättrar tydligheten.
            - Upprepa INTE samtyckeskontexten ordagrant; sammanfatta endast det som behövs.
            - Inga juridiska eller diagnostiska påståenden; detta är allmän information.
            Nedan får du en kort sammanfattning av samtalet. Använd den endast om den är relevant.
            """

            context = f"""Titel: {summary.get('Titel', '')}
            Översikt: {summary.get('Översikt', '')}
            Vanliga risker: {', '.join(summary.get('Vanliga risker', [])[:5])}
            Sällsynta risker: {', '.join(summary.get('Sällsynta risker', [])[:3])}
            Alternativ: {', '.join(summary.get('Alternativ', [])[:3])}
            """

            user_prompt = f"""
            Samtyckeskontext (upprepa inte ordagrant):
            {context}
            Kort sammanfattning av samtalet:
            {history or '(none)'}
            Patientens fråga:
            {question}
            """

        else:
            system_prompt = ""
            user_prompt = ""

        # Call API
        response = self._call_llm(instructions=system_prompt,
                                  user_input=user_prompt)

        return response

    def _extract_output_text(self, resp) -> str:
        txt = getattr(resp, "output_text", None)
        if isinstance(txt, str) and txt.strip():
            return txt.strip()

        chunks = []
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for c in getattr(item, "content", []) or []:
                    if getattr(c, "type", None) in ("output_text", "input_text", "text"):
                        t = getattr(c, "text", None)
                        if t:
                            chunks.append(t)

        return "\n".join(chunks).strip()

    def _call_llm(self, instructions, user_input):
        """Call Large Language Model"""

        # Call LLM
        response = self.client.responses.create(
            model=self.default_model,
            instructions=instructions,
            input=user_input,
        )

        # Extract content
        content = self._extract_output_text(response) or {}
        return content

    def _transcribe(self, path_recording) -> str:
        """Call Speech-to-Text model"""
        audio_file = open(path_recording, "rb")

        # Call API
        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )

        return transcription.text

    def _tts(self, tts_text: str, language: str) -> bytes:
        """Call Text-to-Speech model"""

        tts_text = tts_text.replace("'Title':", "'Procedure':")
        instructions ={"English": """You are a compassionate medical assistant speaking to a patient who is preparing for a surgery
                 or procedure. Read the provided input verbatim—do not add or remove words. Deliver in a warm, calm, reassuring,
                 and conversational tone (avoid a robotic cadence). Pace: ~135–150 wpm; slow down for steps, risks, numbers, 
                 dosages, dates, and names; add brief natural pauses after commas and between list items, and a slightly longer
                 pause (≈300–500 ms) after headings and before lists. Enunciate medical terms clearly. Read acronyms as 
                 letters (e.g., “MRI” → “M-R-I”); if an expansion appears in parentheses, speak the expansion and skip the 
                 parentheses. Numbers/units: read 0.5 as “zero point five”; °C/°F, kg, mg, mL, cm as their full names; “mmHg” 
                 as “millimeters of mercury”; timestamps in 24-hour format as “sixteen thirty”; dates in YYYY-MM-DD as “August
                 27, twenty twenty-five.” Respect inline cues if present—[pause], [slow], [fast], [spell-out], [list],
                 [newline]—apply them but never say the brackets aloud. Address the listener as “you,” use inclusive 
                 language, and keep phrasing non-alarming while conveying confidence. If the text contains a question for 
                 the patient, deliver it gently and leave a brief beat afterward. Do not disclose that you are an AI; avoid 
                 filler words.""",
                       "Svenska": """Du är en varm, lugn och förtroendeingivande medicinsk assistent som talar till en patient 
                inför en operation eller ett medicinskt ingrepp. Läs det givna innehållet ordagrant—lägg inte till eller ta 
                bort något. Använd samtalston (undvik robotlik rytm). Tempo: ca 130–145 ord/min; sakta ner vid steg, risker, 
                siffror, doser, datum och namn; gör korta naturliga pauser efter kommatecken och mellan punktlistor, samt en 
                något längre paus (≈300–500 ms) efter rubriker och före listor. Uttala medicinska termer tydligt. Läs akronymer 
                bokstav för bokstav (t.ex. ”MRI” → ”M-R-I”); om en förklaring finns i parentes, läs förklaringen och utelämna 
                parenteserna. Tal/enheter: läs 0,5 som ”noll komma fem”; säg °C, kg, mg, mL, cm med fullständiga namn; ”mmHg” 
                som ”millimeter kvicksilver”; tider i 24-timmarsformat som ”sexton trettio”; datum i YYYY-MM-DD som ”27 augusti 
                tjugohundratjugofem.” Följ eventuella styrtaggar—[paus], [långsamt], [snabbt], [bokstavera], [lista], 
                [radbryt]—tillämpa dem men uttala aldrig hakparenteserna. Tilltala patienten med ”du”, använd inkluderande språk
                och undvik alarmerande formuleringar samtidigt som du låter trygg. Om texten innehåller en fråga till 
                patienten, läs den mjukt och lämna ett kort uppehåll efteråt. Säg inte att du är en AI; undvik 
                utfyllnadsljud."""

        }
        # Call API
        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice = "ash",
            input = tts_text,
            instructions = instructions[language],
            response_format = "wav"
        )

        return response.content
