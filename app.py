# -*- coding: utf-8 -*-
"""
app.py — Interfaz de chat en Streamlit.
Conecta con backend.py para mantener la lógica de conversación,
historial y resumen de memoria.
"""

import os
import streamlit as st
from backend import (
    crear_cliente,
    enviar_mensaje,
    MODEL_CHAT,
    MODEL_SUMMARY,
    MAX_TOKENS,
    DEFAULT_SYSTEM_PROMPT,
)

# ─── Configuración de la página ─────────────────────────────────────
st.set_page_config(
    page_title="Chat LLM · Asistente IA",
    page_icon="🤖",
    layout="centered",
)

# ─── Estilos CSS personalizados ──────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Globales ─────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Contenedor principal ─────────────────── */
    .block-container {
        max-width: 820px;
        padding-top: 2rem;
    }

    /* ── Header ───────────────────────────────── */
    .header-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 14px;
        padding: 1.5rem 1rem 1.2rem;
        margin-bottom: 1.6rem;
        text-align: center;
    }
    .header-banner .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin: 0 0 0.25rem 0;
    }
    .header-banner .header-sub {
        color: rgba(255,255,255,0.8);
        font-size: 0.92rem;
        margin: 0;
    }

    /* ── Burbujas de chat ─────────────────────── */
    .chat-bubble {
        padding: 0.85rem 1.1rem;
        border-radius: 14px;
        margin-bottom: 0.65rem;
        line-height: 1.55;
        font-size: 0.97rem;
        animation: fadeSlideIn 0.3s ease;
    }
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        margin-left: 18%;
        border-bottom-right-radius: 4px;
    }
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.08);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-right: 18%;
        border-bottom-left-radius: 4px;
    }
    .bubble-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
        opacity: 0.7;
    }

    /* ── Panel lateral (sidebar) ──────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    .sidebar-metric {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }
    .sidebar-metric .metric-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #aaa !important;
    }
    .sidebar-metric .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #a78bfa !important;
    }

    /* ── Animación ────────────────────────────── */
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Botón reset ──────────────────────────── */
    div[data-testid="stSidebar"] button[kind="secondary"] {
        width: 100%;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        margin-top: 0.5rem;
    }

    /* ── Resumen expandible ───────────────────── */
    details {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Obtener API Key de forma segura ─────────────────────────────────
def obtener_api_key() -> str:
    """
    Intenta leer la API key de st.secrets primero y luego de la variable
    de entorno OPENAI_API_KEY. Devuelve cadena vacía si no encuentra nada.
    """
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        key = os.getenv("OPENAI_API_KEY", "")
        return key


# ─── Inicializar session_state ───────────────────────────────────────
def init_state():
    defaults = {
        "historial": [],
        "resumen_memoria": "",
        "total_tokens": 0,
        "client": None,
        "api_key_ok": False,
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ─── Conectar cliente OpenAI ─────────────────────────────────────────
api_key = obtener_api_key()

if api_key:
    if not st.session_state.api_key_ok:
        st.session_state.client = crear_cliente(api_key)
        st.session_state.api_key_ok = True
else:
    st.warning(
        "⚠️ No se encontró la API key. Configúrala en `.streamlit/secrets.toml` "
        "o como variable de entorno `OPENAI_API_KEY`."
    )
    st.stop()

client: object = st.session_state.client  # type: ignore[assignment]


# ─── Header ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="header-banner">'
    '<p class="header-title">🤖 Chat LLM</p>'
    '<p class="header-sub">Asistente especializado en modelos LLM, APIs y Machine Learning</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ─── Sidebar: métricas y controles ───────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Estado de la conversación")

    n_mensajes = len(st.session_state.historial)
    tokens = st.session_state.total_tokens
    tiene_resumen = bool(st.session_state.resumen_memoria.strip())

    st.markdown(
        f"""
        <div class="sidebar-metric">
            <div class="metric-label">Mensajes en historial</div>
            <div class="metric-value">{n_mensajes}</div>
        </div>
        <div class="sidebar-metric">
            <div class="metric-label">Tokens última llamada</div>
            <div class="metric-value">{tokens:,}</div>
        </div>
        <div class="sidebar-metric">
            <div class="metric-label">Límite de tokens</div>
            <div class="metric-value">{MAX_TOKENS:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Indicador de resumen activo
    if tiene_resumen:
        st.markdown("---")
        with st.expander("🧠 Resumen de memoria activo", expanded=False):
            st.write(st.session_state.resumen_memoria)
    else:
        st.caption("🧠 Sin resumen de memoria aún.")

    st.markdown("---")
    st.caption(f"Modelo chat: **{MODEL_CHAT}**")
    st.caption(f"Modelo resumen: **{MODEL_SUMMARY}**")
    st.markdown("---")

    # Editor del system prompt
    st.markdown("### ⚙️ Rol del sistema")
    nuevo_prompt = st.text_area(
        "Edita el comportamiento del asistente:",
        value=st.session_state.system_prompt,
        height=120,
        key="system_prompt_input",
    )
    if nuevo_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = nuevo_prompt

    st.markdown("---")

    # Botón de reset
    if st.button("🗑️  Nueva conversación", use_container_width=True):
        st.session_state.historial = []
        st.session_state.resumen_memoria = ""
        st.session_state.total_tokens = 0
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
        st.rerun()


# ─── Mostrar historial de mensajes ───────────────────────────────────
for msg in st.session_state.historial:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(
            f'<div class="chat-bubble user-bubble">'
            f'<div class="bubble-label">Tú</div>{content}</div>',
            unsafe_allow_html=True,
        )
    elif role == "assistant":
        st.markdown(
            f'<div class="chat-bubble assistant-bubble">'
            f'<div class="bubble-label">Asistente</div>{content}</div>',
            unsafe_allow_html=True,
        )


# ─── Campo de entrada ────────────────────────────────────────────────
user_input = st.chat_input("Escribe tu mensaje…")

if user_input:
    # Mostrar inmediatamente la burbuja del usuario
    st.markdown(
        f'<div class="chat-bubble user-bubble">'
        f'<div class="bubble-label">Tú</div>{user_input}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Pensando…"):
        try:
            resultado = enviar_mensaje(
                client=client,
                mensaje_usuario=user_input,
                historial=st.session_state.historial,
                resumen_memoria=st.session_state.resumen_memoria,
                system_prompt=st.session_state.system_prompt,
            )

            st.session_state.historial = resultado["historial"]
            st.session_state.resumen_memoria = resultado["resumen_memoria"]
            st.session_state.total_tokens = resultado["total_tokens"]

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al consultar el modelo: {e}")
