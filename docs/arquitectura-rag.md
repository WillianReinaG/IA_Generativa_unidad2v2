# Arquitectura orientada a RAG · EcoMarket

## Flujo recomendado

1. **Entrada** del cliente (chat, correo o red social).
2. **Clasificador ligero** (reglas + modelo): si detecta queja grave, fallo técnico o solicitud explícita de persona → **escalamiento humano** (~20 %).
3. **Retriever**: búsqueda en base de conocimiento (pedidos, políticas, fichas de producto).
4. **Prompt aumentado**: instrucciones + documentos recuperados + mensaje del usuario.
5. **LLM** → respuesta fundamentada (~80 % consultas repetitivas).

## Latencia

La recuperación añade latencia frente a un LLM “directo”, pero reduce alucinaciones y alinea las respuestas con políticas reales de EcoMarket.
