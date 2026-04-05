# Fase 2 — Fortalezas, limitaciones y riesgos éticos (EcoMarket)

Este documento se limita a lo que **sí está implementado** en el repositorio `entrega` y al marco de referencia **80 % / 20 %** descrito en el enunciado del proyecto (consultas repetitivas vs. casos que requieren humano), sin añadir funcionalidades futuras.

---

## Marco de referencia (80 % / 20 %)

- **~80 %:** consultas repetitivas (estado de pedido, devoluciones con política fija, etc.), abordables con **prompts + contexto del TOML** en los modos `order` y `return` de `main.py`.  
- **~20 %:** situaciones que el enunciado asocia a **empatía humana y criterio**; en el código, el modo `escalate`, el `repl --mode escalate` y la heurística en `ecomarket/tickets.py` orientan a **escalamiento** y **tickets** en `data/tickets.json`.

El porcentaje **no se calcula** en tiempo de ejecución: es una **guía de diseño**. Lo medible en el repo es la **separación de flujos** (pedido / devolución / escalamiento / REPL).

---

## Fortalezas: ¿Qué hace bien *este* prototipo?

1. **Reducción del tiempo de respuesta**  
   Tras configurar la API, las respuestas llegan en el orden de segundos frente a esperar a un agente.

2. **Disponibilidad continua (mientras el servicio de API esté operativo)**  
   Puedes ejecutar la CLI en cualquier momento; no depende de turnos humanos para generar la primera respuesta.

3. **Manejo de consultas repetitivas típicas**  
   Con el documento de pedidos y la política en `settings-final.toml`, los modos `order` y `return` **atan** la respuesta a ese texto mediante instrucciones explícitas en `ecomarket/messages.py`.

4. **Escalamiento y seguimiento básico**  
   `ecomarket/tickets.py` + `repl` permiten **registrar tickets** y **inyectar** el ID al modelo para que no invente otro número en la misma sesión.

5. **Coherencia en conversaciones largas (REPL)**  
   Se reenvía historial (`complete_chat_messages`) y, si hay ticket activo, un bloque fijo en el system (`append_repl_context`, `format_ticket_context`).

6. **Reproducibilidad académica**  
   Misma configuración de modelo y prompts vía TOML; secretos solo en `.env` (no versionado).

7. **Pruebas sin llamar a la API**  
   `--dry-run` en `order`, `return`, `escalate` y `demo` permite revisar el **system prompt** construido.

---

## Limitaciones: ¿Qué *no* hace o qué puede fallar?

1. **No cubre el “20 % humano” por sí solo**  
   El software **no** sustituye juicio, negociación ni responsabilidad legal; solo **texto** y reglas programadas.

2. **No hay base de datos real de EcoMarket**  
   Pedidos y políticas son **texto de prueba** en el TOML. Si ese texto es incorrecto, el modelo **repetirá** el error de forma convincente.

3. **Dependencia del contexto inyectado**  
   Si falta un dato en el TOML (p. ej. un número de seguimiento), el comportamiento esperado es **no inventar**; aun así, el LLM puede **desviarse** si las instrucciones no se cumplen siempre al 100 %.

4. **Heurística de tickets imperfecta**  
   `needs_escalation_heuristic` usa palabras clave: puede **omitir** quejas no previstas o **activarse** en casos borde. Es un filtro simple, no un clasificador entrenado.

5. **Coste y latencia**  
   Cada turno del `repl` o cada `demo` consume tokens; contextos largos (tabla de pedidos + política + historial) aumentan coste y tiempo.

6. **Alcance de la CLI**  
   No es un chat web ni integración con correo/redes: es una **herramienta de línea de comandos** para demostración y prueba.

---

## Riesgos éticos

### Alucinaciones

- **Riesgo:** El modelo inventa un estado de pedido, una política o un número de ticket distinto del inyectado.  
- **Mitigación en el repo:** Instrucciones en el TOML (“solo usa el documento…”, “no inventes…”) e inyección del ticket real en REPL. **No elimina** el riesgo por completo: hace falta revisión humana en producción y pruebas.

### Sesgo

- **Riesgo:** Tono o contenido que refleje sesgos del modelo base o del texto redactado en los prompts.  
- **Mitigación:** Revisar los textos de `settings-final.toml`, muestrear conversaciones y ajustar instrucciones; el proveedor del LLM puede tener políticas de uso adicionales.

### Privacidad de datos

- **Riesgo:** Enviar a la API de OpenAI datos personales o sensibles en el mensaje del usuario o en el contexto.  
- **Mitigación:** **Minimizar** lo que se pega en el chat de prueba; no usar datos reales de clientes en entregas académicas; leer la política de retención del proveedor; `.env` y `data/` no deben subirse a repositorios públicos con secretos o datos personales (el `.gitignore` ya ignora `.env` y `data/`).

### Impacto laboral

- **Riesgo:** Interpretar el prototipo como “reemplazo” del personal de soporte.  
- **Enfoque alineado al enunciado:** Automatizar **primera línea** y **consultas repetitivas**; el **20 %** y los conflictos graves siguen requiriendo **personas**. El objetivo razonable es **apoyar** al agente (menos carga mecánica), no eliminar el rol sin planificación.

---

## Preguntas de la Fase 2 (respuestas directas)

**Fortalezas:** respuesta rápida, uso 24/7 a nivel de API, buen encaje con consultas repetitivas si el contexto del TOML es correcto, registro de tickets y memoria en REPL, y modo `--dry-run` para auditoría de prompts.

**Limitaciones:** sin BD real, riesgo de errores si el TOML está mal, heurística simple, coste por token, y la CLI no es el producto final multicanal.

**Riesgos éticos:** alucinaciones, sesgo, privacidad al usar APIs de terceros, y uso responsable respecto al trabajo humano (complementar, no sustituir sin criterio).

---

*Proyecto: IA Generativa — Unidad 2 — EcoMarket (`entrega`).*
