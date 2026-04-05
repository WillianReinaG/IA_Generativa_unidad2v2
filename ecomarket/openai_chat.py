from __future__ import annotations

import os

from openai import OpenAI


def complete_chat(
    system: str,
    user: str,
    *,
    model: str,
    temperature: float,
    api_key: str | None = None,
) -> str:
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Crea un archivo .env (ver .env.example) o exporta la variable."
        )
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    choice = response.choices[0].message.content
    return (choice or "").strip()
