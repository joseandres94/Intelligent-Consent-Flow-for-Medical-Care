import tempfile, os, json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal, Dict
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import AIMessage

from .services.ai_service import GRAPH

# Read .env file
load_dotenv()

# Paths definition
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = (BASE_DIR / ".." / "data" / "logs").resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)

# API initialization
app = FastAPI(title="Consent App Backend.")

# CORS configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define session memory
SESSIONS: Dict[str, dict] = {}  # Key: 'session_id', Value: 'state'


# Classes definition
class ChatRequest(BaseModel):
    session_id: str
    text_input: str
    stage: str
    language: Literal["English", "Svenska"] = "English"


class ChatResponse(BaseModel):
    answer: str
    summary: Optional[dict] = None
    stage: Literal["welcome", "summary", "qa"]


class ConsentRecord(BaseModel):
    patient_name: str
    session_id: Optional[str] = None
    method: str  # "typed" | "verbal" | "signature"
    timestamp: str


# Functions definition
def log_event(kind: str, payload: dict):
    now = datetime.now(timezone.utc)
    record = {"kind": kind, "ts": now.isoformat(), **payload}
    path = LOG_DIR / f"{now.date()}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# Functions definition
@app.get("/health")
def health():
    return{"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Get session id
    state = SESSIONS.get(req.session_id, {"session_id": req.session_id, "language": req.language})
    state.update({"user_text": req.text_input, "language": req.language})

    # Check if procedure given
    if not req.text_input.strip():
        raise HTTPException(status_code=400, detail="No procedure given.")

    # Call agent
    result = GRAPH.invoke({"user_text": req.text_input, "language": req.language},
                          config={"configurable": {"thread_id": req.session_id}})

    # Extract content
    state = dict(result)
    answer = ""
    for msg in state.get("messages", []):
        if isinstance(msg, AIMessage):
            answer = msg.content

    # Save log    
    log_event("audit_log",  {"session_id":req.session_id,
                            "user_text": req.text_input,
                            "answer": answer})

    return {"answer": answer, "summary": state.get("summary"), "stage": state.get("stage")}


@app.post("/consent")
def save_consent(cons: ConsentRecord):
    # Save log
    log_event("consent_captured", cons.dict())

    # Return response
    return {"ok": True}


@app.post("/transcribe")
async def transcribe(session_id: str = Form(...),
                     language: Literal["English", "Svenska"] = Form("English"),
                     file: UploadFile = File(...)) -> str:
    # Check if audio given
    if file is None:
        raise HTTPException(status_code=400, detail="Audio not found.")

    # Save to temp file
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            # Call agent
            result = GRAPH.invoke({"stage": "input", "user_text": "",
                                   "path_recording": tmp_path,"language": language},
                                  config={"configurable": {"thread_id": session_id}})

            transcription = result.get("user_text")

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return transcription


@app.post("/tts")
async def tts(req: ChatRequest):
    # Check if text given
    if req.text_input is None:
        raise HTTPException(status_code=400, detail="Text to generate voice not found.")

    try:
        # Call agent
        result = GRAPH.invoke({"user_text": req.text_input,
                               "type": "audio",
                               "language": req.language},
                              config={"configurable": {"thread_id": req.session_id}})

        return Response(result["audio_bytes"], media_type="audio/wav")

    except Exception:
        raise HTTPException(status_code=400, detail="Failed to generate voice.")
