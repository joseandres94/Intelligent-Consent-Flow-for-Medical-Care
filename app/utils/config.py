"""
Configuration settings for the AI Agent Web Generator.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration settings."""

    # Framework Options
    LANGUAGES: List[str] = None

    # API Settings
    API_BASE_URL: str = "http://localhost:8000"
    API_TIMEOUT: int = 300
    API_HEALTH_TIMEOUT: int = 5
    API_CONNECT_TIMEOUT: int = 10
    API_READ_TIMEOUT: int = 600

    # UI Settings
    PAGE_TITLE: str = "AI Agent - Consent Flow Demo"
    PAGE_ICON: str = "🩺"
    LAYOUT: str = "centered"
    INITIAL_SIDEBAR_STATE: str = "collapsed"

    def __post_init__(self):
        """Initialize default values for lists."""
        if self.LANGUAGES is None:
            self.LANGUAGES = [
                "English", "Swedish"
            ]


# Global configuration instance
app_config = AppConfig()


def get_config() -> AppConfig:
    """Get the application configuration."""
    return app_config


def get_custom_css() -> str:
    """Get custom CSS for the application (chat + mic alineados y funcionales)."""
    return """
        <style>
          /* ===== Header transparente (sin barra blanca) ===== */
          header, div[data-testid="stHeader"]{
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
          }
        
          /* ===== Ocultar botón Deploy / toolbar extra ===== */
          /* Botón Deploy (versiones nuevas) */
          a[data-testid="stDeployButton"],
          .stDeployButton { display: none !important; }
        
          /* Toolbar del header (si existe en tu build) */
          div[data-testid="stToolbar"]{ background: transparent !important; box-shadow: none !important; }
        
          /* Viewer badge (Streamlit Cloud; clases con hash) */
          div[class^="viewerBadge_"], div[class*="viewerBadge_"]{ display: none !important; }
        
          /* Decoración superior (algunas builds añaden una banda) */
          div[data-testid="stDecoration"]{ background: transparent !important; box-shadow: none !important; }
        
          /* ===== Mantener el botón de la sidebar accesible ===== */
          [data-testid="collapsedControl"]{
            position: fixed !important;
            top: 10px !important;
            left: 12px !important;
            z-index: 3000 !important;
            background: rgba(255,255,255,0.92) !important;   /* si la quieres invisible, cámbialo a 'transparent' */
            border: 1px solid rgba(0,0,0,0.06) !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12) !important;
          }
            /* ---------- Layout base ---------- */
            /* NO ocultar el header para poder abrir/cerrar la sidebar */
            /* (El bloque que la ocultaba se ha eliminado) */

            /* Contenedor principal a columna y a altura completa
               (mantiene espacio inferior para que el chat_input no tape contenido) */
            .main .block-container,
            section[data-testid="stMain"] > div.block-container {
              max-width: 960px;
              display: flex !important;
              flex-direction: column !important;
              min-height: 100vh !important;
              gap: .5rem;
              padding-top: .75rem !important;
              padding-bottom: 7.5rem !important; /* que no tape el chat_input */
            }

            /* ---------- Fondo y tipografía ---------- */
            /* Fondo: turquesa muy suave -> blanco */
            .main, .stApp, .appview-container {
              background: linear-gradient(180deg, #8af2e2 0%, #FFFFFF 70%) !important;
              min-height: 100vh;
            }

            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }

            h1, h2, h3 {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-weight: 700;
                color: #40E0D0; /* más legible sobre fondo claro */
            }
            .main h1 {
                font-size: 2.6rem;
                font-weight: 800;
                text-align: left;
                margin: 0 0 .25rem 0;
                /* mantén el acento degradado del título si te gusta;
                   sobre fondo claro funciona bien */
                background: linear-gradient(135deg, #93c5fd 0%, #a78bfa 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            }
            .main p, .main .stMarkdown { color: #1f2937; }

            /* ---------- Mensajes tipo burbuja ---------- */
            [data-testid="stChatMessage"] {
                border-radius: 16px;
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(15,23,42,0.06);
                box-shadow: 0 6px 20px rgba(0,0,0,.08);
                padding: .75rem 1rem;
            }
            [data-testid="stChatMessage"] > div:first-child { margin-right: .5rem; }
            [data-testid="stChatMessage"] .stMarkdown p { margin-bottom: .25rem; }

            /* ---------- Espaciador para empujar al fondo ---------- */
            #push-bottom { margin-top: auto !important; }

            /* ---------- Fila del mic justo encima del chat_input (mantén tus columnas) ---------- */
            .mic-row {
                display: flex; align-items: center; justify-content: flex-end;
                gap: .5rem; padding: .25rem 0 .35rem 0;
            }

            /* ---------- st.audio_input (nativo) ---------- */
            /* Oculta etiqueta del widget */
            div[data-testid="stAudioInput"] label[for] { display: none !important; }

            /* Compactar toolbar y eliminar elementos accesorios (forma de onda/tiempo) */
            div[data-testid="stAudioInput"] [data-testid="stAudioInputWaveform"],
            div[data-testid="stAudioInput"] [data-testid="stAudioInputTimeCode"],
            div[data-testid="stAudioInput"] [data-testid="stAudioInputWaveformTimeCode"] {
                display: none !important;
            }

            /* Botón de grabación redondo tipo FAB */
            div[data-testid="stAudioInput"] [data-testid="stAudioInputActionButton"] button,
            div[data-testid="stAudioInput"] button[aria-label="Record"] {
                min-width: 2.6rem !important;
                width: auto !important;
                height: 2.4rem !important;
                padding: .35rem .7rem !important;
                border-radius: 9999px !important;
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%) !important;
                color: #0b1324 !important; font-weight: 700 !important;
                border: 0 !important;
                box-shadow: 0 6px 18px rgba(59,130,246,.35) !important;
            }

            /* ---------- Chat input (sin padding extra) ---------- */
            [data-testid="stChatInput"] [contenteditable="true"] { padding-right: 0 !important; }

            /* ---------- Scrollbar sutil ---------- */
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: rgba(15,23,42,0.06); border-radius: 4px; }
            ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%); border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #b8c3d1 0%, #7b8aa3 100%); }
        </style>
        """