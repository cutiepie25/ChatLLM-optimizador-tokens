# -*- coding: utf-8 -*-
"""
backend.py — Lógica de conversación con memoria y resumen.
Adaptado del script original de consola para ser consumido por Streamlit.
"""

from openai import OpenAI

# ─── Configuración de modelos ───────────────────────────────────────
MODEL_CHAT = "gpt-4"
MODEL_SUMMARY = "gpt-4"

DEFAULT_SYSTEM_PROMPT = (
    "Eres un experto en creación de modelos LLM, uso de APIs de diferentes modelos, "
    "experto en programación eficiente y machine learning."
)

# Cuántos mensajes recientes conservar al resumir
MENSAJES_RECIENTES = 12
MAX_TOKENS = 8000


# ─── Funciones auxiliares ────────────────────────────────────────────

def crear_cliente(api_key: str) -> OpenAI:
    """Crea y devuelve un cliente OpenAI con la key proporcionada."""
    return OpenAI(api_key=api_key)


def construir_mensajes_para_api(
    resumen: str, historial_reciente: list, system_prompt: str = ""
) -> list:
    """Arma la lista de mensajes que se envía al modelo."""
    prompt = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT
    mensajes = [{"role": "system", "content": prompt}]

    if resumen.strip():
        mensajes.append({
            "role": "system",
            "content": f"Memoria resumida de la conversación anterior:\n{resumen}",
        })

    mensajes.extend(historial_reciente)
    return mensajes


def crear_mensaje_resumen(
    client: OpenAI, resumen_actual: str, mensajes_a_resumir: list
) -> str:
    """Genera un resumen acumulado usando el modelo de resumen."""
    prompt_resumen = [
        {
            "role": "system",
            "content": (
                "Resume la conversación de forma compacta y útil para continuar después. "
                "No inventes información. Conserva objetivos, decisiones, restricciones, "
                "datos importantes y temas abiertos. Devuelve solo el resumen final."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Resumen previo:\n{resumen_actual}\n\n"
                f"Mensajes a resumir:\n{mensajes_a_resumir}"
            ),
        },
    ]

    respuesta = client.chat.completions.create(
        model=MODEL_SUMMARY,
        messages=prompt_resumen,
    )
    return respuesta.choices[0].message.content


def enviar_mensaje(
    client: OpenAI,
    mensaje_usuario: str,
    historial: list,
    resumen_memoria: str,
    system_prompt: str = "",
) -> dict:
    """
    Procesa un mensaje del usuario y devuelve un dict con:
      - respuesta: texto del assistant
      - historial: historial actualizado
      - resumen_memoria: resumen actualizado
      - total_tokens: tokens consumidos en la última llamada
    """
    historial.append({"role": "user", "content": mensaje_usuario})

    mensajes_api = construir_mensajes_para_api(resumen_memoria, historial, system_prompt)

    response = client.chat.completions.create(
        model=MODEL_CHAT,
        messages=mensajes_api,
    )

    respuesta_texto = response.choices[0].message.content
    total_tokens = response.usage.total_tokens

    historial.append({"role": "assistant", "content": respuesta_texto})

    # Si los tokens exceden el límite, resumir la parte antigua
    if total_tokens > MAX_TOKENS:
        parte_antigua = historial[:-MENSAJES_RECIENTES]
        historial = historial[-MENSAJES_RECIENTES:]
        resumen_memoria = crear_mensaje_resumen(
            client, resumen_memoria, parte_antigua
        )

    return {
        "respuesta": respuesta_texto,
        "historial": historial,
        "resumen_memoria": resumen_memoria,
        "total_tokens": total_tokens,
    }
