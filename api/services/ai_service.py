from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated, Literal, Dict, List

# Import functions
from .tools import AIService

# Create AI object
ai_service = AIService()

# Define classes
class State(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    user_text: str
    type: str
    path_recording: str
    audio_bytes: bytes
    language: Literal["English", "Swedish"]
    summary: Dict[str, object]
    stage: str

# Define functions
def history2text(history_msgs: List[BaseMessage], max_history: int) -> str:
    pairs = []
    for msg in history_msgs[-2*max_history:]:
        role = getattr(msg, "type", "")
        content = getattr(msg, "content", "")
        if role == "human":
            pairs.append(f"Q: {content}")
        elif role == "ai":
            pairs.append(f"A: {content}")
    return "\n".join(pairs)


def transcribe_audio(state:State) -> State:
    path_recording = state.get("path_recording")
    if path_recording:
        transcription = ai_service._transcribe(path_recording)
    else:
        raise Exception("No recording path found.")

    return {"user_text": transcription,
            "stage": "input"}


def generate_audio(state:State) -> State:
    tts_text = state.get("user_text")
    language = state.get("language")
    if tts_text:
        audio_bytes = ai_service._tts(tts_text, language)
    else:
        raise Exception("Text not found.")

    return {"audio_bytes": audio_bytes,
            "stage": state.get("stage")}


def build_summary(state: State) -> State:
    user_query = state.get("user_text")
    language = state.get("language", "English")

    # Call LLM
    if user_query:
        response = ai_service._summary(user_query=user_query,
                                       language=language)

        summary = ai_service._parse_summary(response)

        if len(summary) == 0:
            return {"messages": [HumanMessage(content=user_query), AIMessage(content=str(response))],
                    "stage": "welcome"}
        else:
            return {"messages": [HumanMessage(content=user_query), AIMessage(content=str(summary))],
                    "summary": summary,
                    "stage": "summary"}


def answer_qa(state: State) -> State:
    question = state.get("user_text", "Question")
    language = state.get("language", "English")
    history = history2text(state.get("messages") or [], max_history=3)

    # Call LLM
    ai_service.check_availability()
    answer = ai_service._answer_qa(question=question,
                                   language=language,
                                   summary=state.get("summary"),
                                   history=history)

    return {"messages": [HumanMessage(content=question), AIMessage(content=str(answer))],
            "stage": "qa"}


def router(state: State) -> str:
    if state.get("type", "") == "audio":
        return "GenerateAudio"
    elif state.get("stage") == "input" and not state.get("user_text"):
        return "TranscribeAudio"
    elif not "summary" in state:
        return "BuildSummary"
    else:
        return "AnswerQA"

# Define flow
workflow = StateGraph(State)
workflow.add_node("TranscribeAudio", transcribe_audio)
workflow.add_node("GenerateAudio", generate_audio)
workflow.add_node("BuildSummary", build_summary)
workflow.add_node("AnswerQA", answer_qa)

workflow.add_conditional_edges(START, router, {"TranscribeAudio": "TranscribeAudio",
                                               "GenerateAudio": "GenerateAudio",
                                               "BuildSummary": "BuildSummary",
                                               "AnswerQA": "AnswerQA"})

workflow.add_edge("TranscribeAudio", END)
workflow.add_edge("GenerateAudio", END)
workflow.add_edge("BuildSummary", END)
workflow.add_edge("AnswerQA", END)

memory = MemorySaver()
GRAPH = workflow.compile(checkpointer=memory)
