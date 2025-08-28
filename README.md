# Intelligent Consent Flow for Medical Care — Demo

A GenAI‑powered consent assistant that explains a medical procedure in plain language, answers questions via voice or text, and captures informed consent (verbal or digital signature) with full traceability. 

> ⚠️ **Disclaimer**: This is a prototype for evaluation only. It is **not** a medical device, does not provide medical advice, and must be validated by clinical, legal, and privacy teams before real‑world use.

---

## Objectives
- **Consent Summary** from raw notes or ICD‑10/CPT codes using an LLM.
- **Interactive review**: patients ask questions via **voice** or **text**; the system answers in the same modality (text or audio).
- **Consent Capture**: **verbal** (record + transcribe) or **signature** (draw on screen or insert name).
- **Logging & Traceability**: patient data and timestamps stored.
- **Multilingual**: EN / SV.

---

## Repository Structure
```
root/
├── api/                      # FastAPI service (api.py, routers/, schemas.py)
│   ├── api.py                # FastAPI services definition
│   ├── services/             # AI services
│      ├── ai_service.py      # LangGraph Agent
│      └── tools.py           # OpenAI APIs
├── app/                      # Streamlit UI (app.py, utils, views)
│   ├── app.py                # Orchestrates web navigation
│   ├── utils/                # Utilities 
│      ├── config.py          # App configuration and custom CSS
│      ├── ui_helpers.py      # Helpers definition
│      └── i18n.py            # Internazionalitation
│   ├── views/                # Web app pages
│      ├── Chat.py            # Main page
│      └── Home.py            # Home page                   
├── main.py                   # Orchestrates API + UI processes
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment configuration
└── README.md
```

---

## Architecture
```
┌───────────────┐         voice/text         ┌─────────────────┐      REST/WebSocket       ┌───────────────────┐
│   Streamlit   │ ─────────────────────────▶ │     FastAPI    │ ───────────────────────▶  │     OpenAI API    │
│  (frontend)   │ ◀───── TTS playback ─────  │    (backend)   │ ◀─ transcripts / outputs─ │    (LLM/STT/TTS)  │
└───────────────┘                            └────────┬────────┘                           └───────────────────┘
                                                      │ event/log store
                                                      ▼ 

```
- **Streamlit** hosts the chat UI, microphone controls, language selector, and signature pad.
- **FastAPI** exposes endpoints for summarization, chat/Q&A, and consent capture.
- **OpenAI** (configurable) handles LLM, STT (e.g., `gpt-4o-mini-transcribe`), and TTS (e.g., `gpt-4o-mini-tts`).
- All interactions are **logged** with ISO‑8601 timestamps and a per‑session identifier.

---

## Main Features
- Patient‑friendly **summary and Q&A** (reading‑level controlled, locale‑aware).
- **Voice in/voice out**: STT and TTS for user queries.
- **Guardrails**: must confirm understanding (**`agree_consent`**) before capturing consent.
- **Simple demo UI** (Streamlit) + clean **API** (FastAPI) separation.

---

## Technologies Used
- **Python 3.10+**, **Streamlit**, **FastAPI + Uvicorn**, **Pydantic**
- **OpenAI** for LLM/STT/TTS (pluggable STT: Deepgram optional)
- **LangChain / LangGraph** for memory/agent state

---

## Prerequisites
- Python 3.10+, `ffmpeg`
- API keys: `OPENAI_API_KEY`
- Known note: if you hit binary issues, pin `numpy<2` in `requirements.txt`.

---

## Installation & Execution
```bash
# Clone
git clone https://github.com/joseandres94/Intelligent-Consent-for-Medical-Care.git
cd Intelligent-Consent-for-Medical-Care

# Install
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

# Configure
cp .env.example .env   # set OPENAI_API_KEY, DEFAULT_LOCALE, etc.

# Run (starts API :8000 and UI :8501)
python main.py
```

---

## Configuration (.env)
- `OPENAI_API_KEY` — required
- `OPENAI_MODEL` — required
- `PORT_FRONTEND`=8501
- `PORT_BACKEND`=8000
- `BACKEND_URL`=http://127.0.0.1:8000
- `ALLOWED_ORIGINS` — restrict in production

---

## Usage
1. **Introduce your name and select language**
2. **Talk to AI Agent** (Give a procedure) by **voice** or **text**
3. **Generate summary** (plain‑language explanation of procedure, risks, alternatives, rights).
4. **Ask questions** by **voice** or **text**; hear answers.
5. **Confirm understanding** (check box → sets `agree_consent=true`).
6. **Capture consent**:
   - **Verbal**: record 5–10s statement → transcribed + timestamped.
   - **Signature**: draw on canvas or name + timestamp.
7. **Receipt**: JSON log are stored.

---

## API Overview (selected)
- `GET /health` → `{ "ok": true }`
- `POST /chat` → `{ session_id, user_input, language } → { answer, summary, stage }`
- `POST /consent` → `{ session_id, patient_name, method, timestamp} → { "ok": True }`
- `POST /transcribe` → `{ session_id, audio_file } → { transcription }`
- `POST /tts` → { session_id, user_input, language } → { audio_file }`

---

## Important Considerations
- Prototype only; **not** medical advice.
- Use HTTPS + strict CORS in deployment; minimize stored PII.

---

## Roadmap (short)
- Realtime Streaming STT
- PDF receipt generation
- Procedure KB (RAG) with citations
- Clinician dashboard

---

## License
MIT — see `LICENSE`.

## Author
José Andrés Lorenzo — https://github.com/joseandres94

