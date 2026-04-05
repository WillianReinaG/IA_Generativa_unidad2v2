from __future__ import annotations

from typing import Any

CONV_MEMORY_SUPPLEMENT = """Tienes acceso al historial de esta conversación en los mensajes anteriores (turnos user/assistant).
Mantén coherencia y no contradigas respuestas previas. Si el cliente pregunta por el número de ticket y este prompt incluye
un ticket bajo "Estado del sistema", responde con ese ID exacto. Si no hay ticket en el estado del sistema, dilo con claridad
y no inventes un número."""


def _strip(s: str) -> str:
    return (s or "").strip()


def format_ticket_context(ticket: dict[str, Any] | None) -> str:
    if not ticket or not ticket.get("id"):
        return ""
    cid = str(ticket["id"])
    created = str(ticket.get("created_at", ""))
    return (
        f"Estado del sistema: ticket activo del cliente: {cid} (creado el {created}). "
        f"No inventes otro número distinto de este."
    )


def append_repl_context(base_system: str, *, ticket: dict[str, Any] | None = None) -> str:
    parts = [_strip(base_system), CONV_MEMORY_SUPPLEMENT.strip()]
    tc = format_ticket_context(ticket)
    if tc:
        parts.append(tc)
    return "\n\n".join(p for p in parts if p)


def build_order_messages(prompts: dict[str, Any], user_message: str) -> tuple[str, str]:
    kb = _strip(str(prompts.get("orders_database_document", "")))
    inst = _strip(str(prompts.get("order_instruction_prompt", ""))).replace(
        ">>>>>PEDIDOS_ECOMARKET<<<<<", kb
    )
    role = _strip(str(prompts.get("order_role_prompt", "")))
    system = f"{role}\n\n{inst}".strip()
    return system, _strip(user_message)


def build_return_messages(prompts: dict[str, Any], user_message: str) -> tuple[str, str]:
    policy = _strip(str(prompts.get("return_policy_document", "")))
    inst = _strip(str(prompts.get("return_instruction_prompt", ""))).replace(
        ">>>>>POLITICA_DEVOLUCIONES<<<<<", policy
    )
    role = _strip(str(prompts.get("return_role_prompt", "")))
    system = f"{role}\n\n{inst}".strip()
    return system, _strip(user_message)


def build_escalation_messages(prompts: dict[str, Any], user_message: str) -> tuple[str, str]:
    msg = _strip(user_message)
    inst = _strip(str(prompts.get("escalation_instruction_prompt", ""))).replace(
        ">>>>>CONTENT<<<<<", msg
    )
    role = _strip(str(prompts.get("escalation_role_prompt", "")))
    system = f"{role}\n\n{inst}".strip()
    user = "Genera la respuesta al cliente en español (México), breve y empática."
    return system, user


def build_escalation_system_repl(
    prompts: dict[str, Any],
    *,
    ticket: dict[str, Any] | None = None,
) -> str:
    """System prompt para REPL con historial (sin incrustar el mensaje actual en el system)."""
    role = _strip(str(prompts.get("escalation_role_prompt", "")))
    inst = _strip(str(prompts.get("escalation_instruction_multiturn", "")))
    if not inst:
        inst = (
            "La conversación previa está en el historial (mensajes usuario/asistente). "
            "Responde al último mensaje del cliente con empatía y alineación a EcoMarket."
        )
    base = f"{role}\n\n{inst}".strip()
    return append_repl_context(base, ticket=ticket)
