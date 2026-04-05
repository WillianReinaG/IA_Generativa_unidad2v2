# IA Generativa — Unidad 2 · EcoMarket (chatbot de atención al cliente)

Proyecto de **ingeniería de prompts** para EcoMarket (comercio electrónico sostenible), basado en la estructura de configuración del repositorio de referencia [avila196/prompt-engineering-sample](https://github.com/avila196/prompt-engineering-sample/blob/main/settings-final.toml).

## Contenido

| Archivo | Descripción |
|---------|-------------|
| `settings-final.toml` | Modelo, temperatura y bloques de prompts (rol, instrucciones, base de conocimiento, ejemplos, razonamiento y salida esperada). |
| `docs/arquitectura-rag.md` | Resumen de arquitectura RAG y flujo 80 % automatizable / 20 % humano. |

## Uso

Los valores en `[general]` y los textos en `[prompts]` pueden cargarse desde una aplicación que lea TOML (por ejemplo Python con `tomllib` / `tomli`). En producción, el documento de pedidos y la política de devoluciones vivirían en un vector store o API; aquí se incluyen como **datos de prueba** embebidos en el mismo estilo que el ejemplo de la asignatura.

## Autor / curso

Entrega — MIAA · IA Generativa.
