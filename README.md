# IA Generativa — Unidad 2 · EcoMarket (chatbot de atención al cliente)

Proyecto de **ingeniería de prompts** para EcoMarket, con **CLI en Python** que lee `settings-final.toml` y llama a la **API de Chat Completions de OpenAI**.

Estructura inspirada en [avila196/prompt-engineering-sample](https://github.com/avila196/prompt-engineering-sample/blob/main/settings-final.toml).

## Requisitos

- **Python 3.10+** (recomendado **3.11+** para `tomllib` en la biblioteca estándar; con 3.10 se instala `tomli` vía `requirements.txt`).
- Cuenta OpenAI y **API key** con acceso a modelos configurados (p. ej. `gpt-4o` o `gpt-4o-mini`).

## Instalación (venv)

En PowerShell, desde esta carpeta (`entrega`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y define `OPENAI_API_KEY`. Opcional: `OPENAI_MODEL=gpt-4o-mini` para pruebas más económicas.

## Contenido del repositorio

| Ruta | Descripción |
|------|-------------|
| `settings-final.toml` | Modelo, temperatura y prompts + base de conocimiento de prueba. |
| `ecomarket/` | Paquete: carga TOML, sustituye placeholders, llamada a OpenAI. |
| `main.py` | Interfaz de línea de comandos. |
| `requirements.txt` | Dependencias. |
| `.env.example` | Plantilla de variables de entorno (no incluye secretos). |
| `docs/arquitectura-rag.md` | Notas de arquitectura RAG y 80 % / 20 % humano. |

## Uso de la CLI

```powershell
# Sin gastar tokens: ver el system prompt (truncado) y el mensaje de usuario
python main.py order -m "¿Estado del pedido ECO-2025-001923?" --dry-run

# Con API key en .env
python main.py order -m "Mi seguimiento es ECO-2025-001923, ¿qué pasa?"
python main.py return -m "Quiero devolver la lámpara del pedido ECO-2025-001968, caja sellada."
python main.py escalate -m "Me cobraron dos veces y no puedo entrar a mi cuenta."

# Varios ejemplos tomados del TOML
python main.py demo

# Chat interactivo (modo pedido, devolución o escalamiento)
python main.py repl --mode order
```

Opciones globales: `--settings`, `--model` (van **antes** del subcomando, p. ej. `python main.py --model gpt-4o-mini order -m "hola"`).  
`--dry-run` va en cada subcomando: `order`, `return`, `escalate` y `demo` (en `demo`, solo imprime los mensajes de ejemplo sin llamar a la API).

## Autor / curso

Entrega — MIAA · IA Generativa.
