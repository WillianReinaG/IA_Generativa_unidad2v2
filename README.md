# IA Generativa — Unidad 2 · EcoMarket (chatbot de atención al cliente)

Proyecto de **ingeniería de prompts** para EcoMarket, con **CLI en Python** que lee `settings-final.toml` y llama a la **API de Chat Completions de OpenAI**.


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
| `ecomarket/` | Paquete: carga TOML, sustitución de placeholders, OpenAI, tickets en disco. |
| `ecomarket/tickets.py` | Persistencia en `data/tickets.json` (`create_ticket`, `get_ticket`, `list_tickets_for_session`). |
| `main.py` | Interfaz de línea de comandos. |
| `data/` | Generada al crear tickets (ignorada en git; no subir datos locales). |
| `requirements.txt` | Dependencias. |
| `.env.example` | Plantilla de variables de entorno (no incluye secretos). |
| `docs/arquitectura-rag.md` | Notas de arquitectura RAG y 80 % / 20 % humano. |
| `docs/FASE1_seleccion_modelo.md` | Fase 1: modelo usado, enfoque híbrido, arquitectura y herramientas del repo. |
| `docs/FASE2_fortalezas_limitaciones_eticos.md` | Fase 2: fortalezas, limitaciones y riesgos éticos (alcance del prototipo). |

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

### REPL: memoria de conversación y tickets

En `repl`, cada sesión tiene un `session_id` (UUID) y se reenvía a OpenAI el **historial** de turnos `user` / `assistant` (últimos 20 mensajes).

- Se crea ticket si el mensaje encaja en la **heurística de quejas / atención humana** (palabras como “queja”, “reclamo”, “no me llegó”, “hablar con alguien”, “fraude”, etc.; ver `ecomarket/tickets.py`) **o**, en `--mode escalate`, si el mensaje tiene **≥ 8 caracteres** y no es un saludo trivial (“hola”, “gracias”, …).
- Si ya había un ticket y llega **otra queja** con heurística positiva, se registra un **ticket nuevo** y el contexto pasa a ese id. Las preguntas solo por el número de ticket **no** abren otro ticket.
- En consola verás líneas `(Sistema) Ticket registrado: …` al crear uno.
- El id activo se inyecta en el **system prompt** (“Estado del sistema: ticket activo…”) para que el modelo no invente otro número.
- Prueba típica (con API key configurada):

```powershell
python main.py repl --mode escalate
```

1. Escribe un mensaje largo o con palabras clave, p. ej.: `Me cobraron dos veces y no puedo entrar a mi cuenta.`  
2. Luego: `¿Cuál es el número de mi ticket?`  
La respuesta debe repetir el **mismo** `TKT-…` guardado en disco.

Opciones globales: `--settings`, `--model` (van **antes** del subcomando, p. ej. `python main.py --model gpt-4o-mini order -m "hola"`).  
`--dry-run` va en cada subcomando: `order`, `return`, `escalate` y `demo` (en `demo`, solo imprime los mensajes de ejemplo sin llamar a la API).

## Autor / curso

Entrega — MIAA · IA Generativa.
