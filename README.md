# ChatLLM - Optimizador de Tokens

Esta aplicación implementa un sistema conversacional basado en modelos LLM capaz de mantener contexto dinámico mediante gestión inteligente de memoria. El sistema permite interactuar con un modelo de lenguaje avanzado conservando coherencia conversacional a través de historial reciente y memoria resumida.

## Arquitectura

La arquitectura se basa en tres componentes principales:

- **Historial conversacional reciente:** conserva los últimos mensajes completos entre el usuario y el asistente para mantener continuidad inmediata.

- **Memoria resumida:** cuando la conversación supera cierto límite de tokens, los mensajes antiguos son comprimidos automáticamente en un resumen contextual que preserva información relevante como objetivos, decisiones, restricciones y temas tratados.

- **Construcción dinámica de contexto:** en cada llamada al modelo se reconstruye el contexto completo enviando instrucciones del sistema, memoria resumida e historial reciente.

## Optimización de Tokens

La aplicación implementa estrategias de optimización de tokens para evitar crecimiento descontrolado del contexto, reduciendo costos y previniendo superar los límites del modelo. En lugar de eliminar mensajes antiguos, el sistema utiliza técnicas de compresión semántica mediante resúmenes automáticos generados por el propio LLM.

## Funcionalidades

- Gestión dinámica de conversaciones.
- Persistencia contextual mediante memoria resumida.
- Optimización automática de tokens.
- Separación entre contexto permanente y contexto reciente.
- Integración con modelos GPT mediante API.
- Arquitectura preparada para integrarse con interfaces gráficas como Streamlit.

## Objetivo

Este enfoque replica una de las estrategias fundamentales utilizadas en sistemas reales basados en inteligencia artificial conversacional, donde la “memoria” no existe de forma nativa en el modelo, sino que debe ser diseñada y administrada desde la aplicación.

---

_Este resumen fue elaborado con ayuda de la IA: ChatLLM-optimizador-tokens._
