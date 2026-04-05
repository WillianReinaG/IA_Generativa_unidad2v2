"""
CLI EcoMarket: prueba los prompts contra la API de OpenAI.

Ejemplos:
  python main.py order -m "¿Estado del pedido ECO-2025-001923?"
  python main.py return -m "Quiero devolver pasta dental abierta del ECO-2025-002001"
  python main.py escalate -m "Me cobraron doble y no entro a mi cuenta"
  python main.py demo
  python main.py repl --mode order
  python main.py repl --mode escalate   # memoria + tickets en data/tickets.json
  python main.py order -m "Hola" --dry-run   # --dry-run va al final del subcomando order
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

from ecomarket.load_settings import default_settings_path, load_settings
from ecomarket.messages import (
    append_repl_context,
    build_escalation_messages,
    build_escalation_system_repl,
    build_order_messages,
    build_return_messages,
)
from ecomarket.openai_chat import complete_chat, complete_chat_messages
from ecomarket.tickets import create_ticket, needs_escalation_heuristic


def _general(cfg: dict) -> tuple[str, float]:
    g = cfg.get("general") or {}
    model = os.environ.get("OPENAI_MODEL") or str(g.get("model", "gpt-4o"))
    temp = float(g.get("temperature", 0))
    return model, temp


def _prompts(cfg: dict) -> dict:
    return cfg.get("prompts") or {}


def cmd_order(args: argparse.Namespace, cfg: dict) -> int:
    p = _prompts(cfg)
    system, user = build_order_messages(p, args.message)
    return _run(args, cfg, system, user)


def cmd_return(args: argparse.Namespace, cfg: dict) -> int:
    p = _prompts(cfg)
    system, user = build_return_messages(p, args.message)
    return _run(args, cfg, system, user)


def cmd_escalate(args: argparse.Namespace, cfg: dict) -> int:
    p = _prompts(cfg)
    system, user = build_escalation_messages(p, args.message)
    return _run(args, cfg, system, user)


def _run(args: argparse.Namespace, cfg: dict, system: str, user: str) -> int:
    model, temperature = _general(cfg)
    if args.model:
        model = args.model
    if args.dry_run:
        head = system[:2000]
        tail_note = "\n... [truncado]\n" if len(system) > 2000 else "\n"
        print("--- system ---\n", head, tail_note, sep="")
        print("--- user ---\n", user, sep="")
        return 0
    try:
        out = complete_chat(system, user, model=model, temperature=temperature)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    print(out)
    return 0


def cmd_demo(args: argparse.Namespace, cfg: dict) -> int:
    p = _prompts(cfg)
    demos: list[tuple[str, str, str]] = [
        (
            "pedido",
            "order",
            (p.get("order_example_customer_message") or "").strip(),
        ),
        (
            "devolución (elegible)",
            "return",
            (p.get("return_example_customer_eligible") or "").strip(),
        ),
        (
            "devolución (higiene)",
            "return",
            (p.get("return_example_customer_not_eligible") or "").strip(),
        ),
        (
            "escalamiento",
            "escalate",
            (p.get("escalation_example_customer_message") or "").strip(),
        ),
    ]
    model, temperature = _general(cfg)
    if args.model:
        model = args.model
    for label, kind, msg in demos:
        print(f"\n=== Demo: {label} ===\nCliente:\n{msg}\n")
        if args.dry_run:
            continue
        if kind == "order":
            system, user = build_order_messages(p, msg)
        elif kind == "return":
            system, user = build_return_messages(p, msg)
        else:
            system, user = build_escalation_messages(p, msg)
        try:
            out = complete_chat(system, user, model=model, temperature=temperature)
        except Exception as e:
            print(e, file=sys.stderr)
            return 1
        print("Asistente:\n", out)
    return 0


MAX_REPL_HISTORY_MESSAGES = 20  # pares user/assistant recientes (límite aproximado de contexto)


def cmd_repl(args: argparse.Namespace, cfg: dict) -> int:
    p = _prompts(cfg)
    mode = args.mode
    model, temperature = _general(cfg)
    if args.model:
        model = args.model
    session_id = str(uuid.uuid4())
    history: list[dict] = []
    active_ticket: dict | None = None

    print(f"EcoMarket REPL ({mode}) — modelo {model}. Sesión: {session_id[:8]}…")
    print("Memoria de conversación activa. Escribe 'salir' para terminar.\n")
    while True:
        try:
            line = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line or line.lower() in ("salir", "exit", "quit"):
            return 0

        # Ticket: heurística de escalamiento, o modo escalate con mensaje sustancial (evita "hola" vacío).
        qualify_ticket = needs_escalation_heuristic(line) or (
            mode == "escalate" and len(line.strip()) >= 30
        )
        if qualify_ticket and active_ticket is None:
            active_ticket = create_ticket(session_id, line)

        if mode == "order":
            base_system, _dupe = build_order_messages(p, line)
            system = append_repl_context(base_system, ticket=active_ticket)
            user_content = line
        elif mode == "return":
            base_system, _dupe = build_return_messages(p, line)
            system = append_repl_context(base_system, ticket=active_ticket)
            user_content = line
        else:
            system = build_escalation_system_repl(p, ticket=active_ticket)
            user_content = line

        messages: list[dict] = [
            {"role": "system", "content": system},
            *history,
            {"role": "user", "content": user_content},
        ]

        try:
            out = complete_chat_messages(messages, model=model, temperature=temperature)
        except Exception as e:
            print(e, file=sys.stderr)
            continue

        history.extend(
            [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": out},
            ]
        )
        if len(history) > MAX_REPL_HISTORY_MESSAGES:
            history = history[-MAX_REPL_HISTORY_MESSAGES:]

        print(f"Asistente: {out}\n")


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="EcoMarket — chat de prueba con OpenAI")
    parser.add_argument(
        "--settings",
        type=Path,
        default=None,
        help=f"Ruta a settings-final.toml (por defecto: {default_settings_path()})",
    )
    parser.add_argument("--model", default=None, help="Sobrescribe el modelo del TOML / OPENAI_MODEL")

    sub = parser.add_subparsers(dest="command", required=True)

    dry_help = "No llama a la API; solo muestra contexto construido (o en demo, solo los mensajes de cliente)"

    p_order = sub.add_parser("order", help="Consulta de estado de pedido")
    p_order.add_argument("-m", "--message", required=True, help="Mensaje del cliente")
    p_order.add_argument("--dry-run", action="store_true", help=dry_help)
    p_order.set_defaults(func=cmd_order)

    p_ret = sub.add_parser("return", help="Devoluciones")
    p_ret.add_argument("-m", "--message", required=True)
    p_ret.add_argument("--dry-run", action="store_true", help=dry_help)
    p_ret.set_defaults(func=cmd_return)

    p_esc = sub.add_parser("escalate", help="Derivación / casos sensibles")
    p_esc.add_argument("-m", "--message", required=True)
    p_esc.add_argument("--dry-run", action="store_true", help=dry_help)
    p_esc.set_defaults(func=cmd_escalate)

    p_demo = sub.add_parser("demo", help="Ejecuta varios mensajes de ejemplo del TOML")
    p_demo.add_argument("--dry-run", action="store_true", help=dry_help)
    p_demo.set_defaults(func=cmd_demo)

    p_repl = sub.add_parser("repl", help="Modo interactivo")
    p_repl.add_argument("--mode", choices=("order", "return", "escalate"), default="order")
    p_repl.set_defaults(func=cmd_repl)

    args = parser.parse_args()
    path = args.settings or default_settings_path()
    if not path.is_file():
        print(f"No se encuentra el archivo de configuración: {path}", file=sys.stderr)
        return 1
    cfg = load_settings(path)
    return int(args.func(args, cfg))


if __name__ == "__main__":
    raise SystemExit(main())
