from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


def _require_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Crea un archivo .env (ver .env.example) o exporta la variable."
        )
    return key


def complete_chat_messages(
    messages: list[dict[str, Any]],
    *,
    model: str,
    temperature: float,
    api_key: str | None = None,
) -> str:
    """Envía una lista de mensajes OpenAI (roles: system, user, assistant, …)."""
    if not messages:
        raise ValueError("messages no puede estar vacío")
    client = OpenAI(api_key=_require_key(api_key))
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    choice = response.choices[0].message.content
    return (choice or "").strip()


def complete_chat(
    system: str,
    user: str,
    *,
    model: str,
    temperature: float,
    api_key: str | None = None,
) -> str:
    """Compatibilidad: un solo turno system + user."""
    return complete_chat_messages(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        model=model,
        temperature=temperature,
        api_key=api_key,
    )
