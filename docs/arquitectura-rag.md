# FASE 3: Aplicación de la Ingeniería de Prompts

## 1. Introducción

En esta fase se diseñan prompts efectivos para interactuar con el modelo de IA, con el objetivo de mejorar la calidad, precisión y utilidad de las respuestas en el sistema de atención al cliente de EcoMarket.

Se aplican principios de ingeniería de prompts como:

* Definición de rol del modelo
* Inclusión de contexto
* Claridad en la instrucción
* Manejo de condiciones
* Estructuración de la respuesta

---

## 2. Diseño de prompts

### 2.1 Prompt: Consulta de estado de pedido

#### 🔹 Versión básica

```text
Dame el estado del pedido 12345.
```

#### 🔹 Versión mejorada (ingeniería de prompts)

```text
Actúa como un agente de servicio al cliente amable y profesional de EcoMarket.

Tu tarea es proporcionar el estado actual del pedido con número de seguimiento "{{tracking_number}}", utilizando exclusivamente la información contenida en la base de datos proporcionada.

Instrucciones:
- Indica el estado actual del pedido.
- Proporciona la fecha estimada de entrega.
- Incluye información de seguimiento si está disponible.
- Si el pedido está retrasado, ofrece una disculpa y explica brevemente la situación.
- Si no encuentras el pedido, indica claramente que no existe en la base de datos.

Formato de respuesta:
Estado del pedido: ...
Fecha estimada: ...
Mensaje adicional: ...
```

---

### 2.2 Base de datos simulada (ejemplo)

```python
pedidos = [
    {"id": "12345", "estado": "En tránsito", "fecha": "2026-04-05"},
    {"id": "12346", "estado": "Entregado", "fecha": "2026-04-01"},
    {"id": "12347", "estado": "Retrasado", "fecha": "2026-04-10"},
    {"id": "12348", "estado": "Procesando", "fecha": "2026-04-06"},
    {"id": "12349", "estado": "En tránsito", "fecha": "2026-04-07"},
    {"id": "12350", "estado": "Cancelado", "fecha": "N/A"},
    {"id": "12351", "estado": "Entregado", "fecha": "2026-03-30"},
    {"id": "12352", "estado": "En tránsito", "fecha": "2026-04-08"},
    {"id": "12353", "estado": "Retrasado", "fecha": "2026-04-12"},
    {"id": "12354", "estado": "Procesando", "fecha": "2026-04-09"}
]
```

---

### 2.3 Prompt: Devolución de producto

```text
Actúa como un agente de atención al cliente empático de EcoMarket.

Tu tarea es guiar al cliente en el proceso de devolución de un producto.

Reglas:
- No se permiten devoluciones de productos perecederos ni de higiene.
- Si el producto es elegible, explica claramente los pasos de devolución.
- Si no es elegible, responde de forma empática y explica la razón.

Formato:
Resultado: (Aprobado / No aprobado)
Explicación: ...
Pasos a seguir: ...
```

---

## 3. Implementación en Python (simulación funcional)

```python
def buscar_pedido(tracking_number, base_datos):
    for pedido in base_datos:
        if pedido["id"] == tracking_number:
            return pedido
    return None


def generar_respuesta_pedido(tracking_number):
    pedido = buscar_pedido(tracking_number, pedidos)

    if pedido:
        estado = pedido["estado"]
        fecha = pedido["fecha"]

        if estado == "Retrasado":
            mensaje = "Lamentamos el retraso. Estamos trabajando para entregarlo lo antes posible."
        else:
            mensaje = "Tu pedido está en proceso normal."

        return f"""
Estado del pedido: {estado}
Fecha estimada: {fecha}
Mensaje adicional: {mensaje}
"""
    else:
        return "El pedido no se encuentra en la base de datos."
```

---

## 4. Ejemplo de uso

```python
print(generar_respuesta_pedido("12347"))
```

---

## 5. Estructura del repositorio (GitHub)

```plaintext
ecoassist-rag/
│
├── README.md
├── fase1.md
├── fase2.md
├── fase3.md
│
├── data/
│   └── pedidos.json
│
├── src/
│   ├── rag_simulation.py
│   └── prompts.py
│
├── notebooks/
│   └── demo.ipynb
│
└── requirements.txt
```

---

## 6. Ejemplo de archivo prompts.py

```python
prompt_pedido = """
Actúa como un agente de servicio al cliente amable...
"""

prompt_devolucion = """
Actúa como un agente empático...
"""
```

---

## 7. Justificación técnica

El uso de prompts estructurados permite:

* Mejorar la precisión de las respuestas
* Reducir ambigüedad
* Controlar el comportamiento del modelo
* Adaptar el sistema a distintos escenarios

La incorporación de contexto (base de datos simulada) demuestra el principio fundamental de RAG: **responder con información real y no inventada**.

---

## 8. Conclusión

La correcta aplicación de la ingeniería de prompts permite maximizar el rendimiento del modelo de IA, garantizando respuestas coherentes, útiles y alineadas con las necesidades del negocio.

Esta fase demuestra cómo la interacción entre usuario y modelo puede ser optimizada mediante instrucciones claras, contexto relevante y estructuras bien definidas.
