# Fase 1 — Selección y justificación del modelo (EcoMarket)

## Aviso

Los nombres de modelo (**GPT-4o**, **GPT-4o mini**, **GPT-4**) se citan **solo en coherencia con la configuración real de este repositorio** (`settings-final.toml` y, si aplica, `OPENAI_MODEL` en `.env`). No implican recomendación comercial ni exclusión de otros proveedores.

---

## ¿Qué modelo de IA generativa usa este proyecto?

| Dónde se define | Valor en el repositorio |
|-----------------|-------------------------|
| Modelo por defecto | **`gpt-4o`** (`[general]` en `settings-final.toml`) |
| Modelos listados como alternativas en configuración | **`gpt-4o-mini`**, **`gpt-4o`**, **`gpt-4`** (`chat_models` en el mismo archivo) |
| Sobrescrito en tiempo de ejecución | Variable de entorno **`OPENAI_MODEL`** (p. ej. `gpt-4o-mini`), leída en `main.py` vía `_general()` |

En conjunto, el núcleo es un **modelo de lenguaje grande (LLM)** accesible por la **API de Chat Completions de OpenAI**. No hay en este repo **fine-tuning** propio ni un segundo modelo entrenado aparte: el comportamiento se controla con **prompts** y con **texto de contexto inyectado**.

---

## ¿Qué tipo de solución es la más adecuada *en este trabajo*?

Es una solución **híbrida** en el sentido siguiente:

1. **LLM (GPT-4o u otro de la lista anterior, según configuración)**  
   Genera el texto de respuesta, sigue el rol y las instrucciones, y mantiene coherencia conversacional (especialmente en `repl` con historial).

2. **Conocimiento factual acotado que no viene “de memoria” del modelo**  
   - **Pedidos y política de devoluciones:** fragmentos sustituidos en el prompt desde `settings-final.toml` (`orders_database_document`, `return_policy_document`) mediante `ecomarket/messages.py`.  
   - **Tickets:** identificadores y metadatos generados y guardados por el programa en `data/tickets.json` (`ecomarket/tickets.py`) e **inyectados** en el mensaje de sistema para que el modelo cite el mismo número.

Esa combinación (**LLM + contexto externo fijado por el sistema**) es el híbrido que implementa el repositorio: el modelo **redacta**; los **datos de prueba y tickets** los aporta el código y los archivos locales.

---

## ¿Por qué este enfoque y no otro *solo con LLM* o *solo reglas*?

| Necesidad | Cómo lo cubre *este* proyecto |
|-----------|--------------------------------|
| **Precisión en pedidos y políticas** | Las instrucciones obligan a usar **solo** el texto del registro de pedidos o la política incrustada en el prompt. El LLM no debe inventar estados ni normas que no estén ahí. |
| **Fluidez y tono** | El LLM reformula en español, responde a variaciones del cliente y mantiene el hilo en el `repl` (historial `user`/`assistant`). |
| **Solo reglas / sin LLM** | No está implementado: el repo apuesta por lenguaje natural con control vía prompts. |
| **Fine-tuned LLM propio** | No está en el repositorio: no hay dataset de entrenamiento ni pipeline de afinado; la “personalización” es por **prompt engineering** y **contexto inyectado**. |

---

## ¿Cuál es la arquitectura *tal como está en el repositorio*?

```
Usuario → main.py (CLI: order | return | escalate | demo | repl)
              │
              ├─ load_settings → settings-final.toml ([general] + [prompts])
              ├─ messages.py → arma system/user (placeholders → documentos del TOML)
              ├─ tickets.py → lectura/escritura data/tickets.json (REPL + heurística)
              └─ openai_chat.py → API OpenAI (chat.completions)
                        │
                        ▼
                 Respuesta al usuario
```

- **Base de conocimiento de prueba:** vive en **`settings-final.toml`** (no hay conexión a una BD SQL en este código).  
- **Persistencia de tickets:** **`data/tickets.json`**, creada en tiempo de ejecución.  
- **Integración con catálogo/envíos reales de EcoMarket:** **no está implementada** en este repositorio; el conocimiento operativo simulado está en `settings-final.toml` y los tickets en `data/tickets.json`.

---

## Herramientas que incluye el repositorio: para qué sirven y por qué se eligieron

| Herramienta / componente | Para qué ayuda |
|--------------------------|----------------|
| **Python 3.10+** | Lenguaje del CLI y del paquete `ecomarket`. |
| **`openai` (SDK)** | Llamadas estándar a la API de chat; evita implementar HTTP a mano. |
| **`python-dotenv`** | Carga `OPENAI_API_KEY` y `OPENAI_MODEL` desde `.env` sin hardcodear secretos. |
| **`tomllib` / `tomli`** | Leer `settings-final.toml` (modelo, temperatura, textos largos de prompts y KB de prueba). |
| **`settings-final.toml`** | Un solo lugar para modelo (`gpt-4o` por defecto), `temperature = 0` (respuestas más estables) y textos de política/pedidos. |
| **`main.py`** | Orquesta modos de prueba y el `repl` con memoria y reglas de ticket. |
| **`ecomarket/messages.py`** | Sustituye marcadores del TOML por el documento correcto y añade memoria/ticket al system en REPL. |
| **`ecomarket/tickets.py`** | Crea y lista tickets en disco; heurística de “queja” alineada con escalamiento. |
| **`ecomarket/openai_chat.py`** | Centraliza la llamada al modelo (`complete_chat` / `complete_chat_messages`). |

---

## Justificación breve (costo, escalabilidad, integración, calidad) *aplicada a lo construido*

| Criterio | Relación con este repo |
|----------|-------------------------|
| **Costo** | Pago por uso de la API; puedes bajar coste usando **`OPENAI_MODEL=gpt-4o-mini`** sin cambiar el resto del código. |
| **Escalabilidad** | Cada comando o turno del `repl` implica una llamada a la API; el volumen depende de cuotas del proveedor y del tamaño del contexto enviado. |
| **Integración** | Archivo TOML + JSON local + variables de entorno: poca fricción para reproducir en otra máquina con venv y `pip install -r requirements.txt`. |
| **Calidad de respuesta** | `temperature = 0` y reglas explícitas en prompts reducen variación; la calidad factual del pedido depende del texto del TOML y de no mezclar datos erróneos ahí. |

---

## Preguntas de la Fase 1 (resumen de respuestas)

1. **¿Qué tipo de modelo es el más adecuado?**  
   **LLM de propósito general vía API** (en este proyecto: familia configurada en `settings-final.toml`, por defecto **GPT-4o**), en esquema **híbrido** con **texto de contexto inyectado** (TOML + tickets en JSON).

2. **¿Por qué este modelo y no otro?**  
   Para **precisión** en pedidos/políticas se apoya en **documentos en el prompt**, no en suposiciones del modelo; para **fluidez** y diálogo multi-turno se usa la capacidad del LLM. No se usa otro paradigma (p. ej. solo reglas) porque el código entregado está centrado en **Chat Completions**.

3. **¿Arquitectura propuesta?**  
   La descrita arriba: **CLI Python → TOML + (opcional) tickets.json → API OpenAI**. No hay BD de productos ni envíos conectada en el código actual.

4. **¿Propósito general o afinado con datos de empresa?**  
   **Propósito general** del proveedor, **guiado** por prompts y por los textos de empresa que tú defines en `settings-final.toml` y por el estado generado en `tickets.py`. **No** hay fine-tuning en el repo.

---

*Proyecto: IA Generativa — Unidad 2 — EcoMarket (`entrega`).*
