import os
import streamlit as st
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Define helper functions
def api_get(path:str, **kwargs):
    url = f"{BACKEND_URL}{path}"
    return st.session_state.http.get(url, timeout=kwargs.pop("timeout", 20), **kwargs)


def api_post(path:str, json=None, **kwargs):
    url = f"{BACKEND_URL}{path}"
    return st.session_state.http.post(url, json=json, timeout=kwargs.pop("timeout", 90), **kwargs)


def check_backend() -> None:
    try:
        r = api_get("/health")
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        detail = None
        if e.response is not None:
            try:
                detail=e.response.json()
            except Exception:
                detail=e.response.text
        st.error(f"Couldn't connect with backend (HTTP): {detail or e}")
        st.stop()

    except Exception as e:
        st.error(f"Couldn't connect with backend: {e}")
        st.stop()