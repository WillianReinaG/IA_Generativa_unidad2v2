from __future__ import annotations

from typing import Any


def _strip(s: str) -> str:
    return (s or "").strip()


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
