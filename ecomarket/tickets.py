from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TICKETS_FILE = DATA_DIR / "tickets.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not TICKETS_FILE.exists():
        TICKETS_FILE.write_text('{"tickets": []}', encoding="utf-8")


def _load_all() -> list[dict[str, Any]]:
    _ensure_data_dir()
    raw = TICKETS_FILE.read_text(encoding="utf-8")
    data = json.loads(raw)
    return list(data.get("tickets", []))


def _save_all(tickets: list[dict[str, Any]]) -> None:
    _ensure_data_dir()
    TICKETS_FILE.write_text(
        json.dumps({"tickets": tickets}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_ticket(session_id: str, summary: str) -> dict[str, Any]:
    tid = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    rec: dict[str, Any] = {
        "id": tid,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "summary": (summary or "").strip()[:500],
        "status": "open",
    }
    tickets = _load_all()
    tickets.append(rec)
    _save_all(tickets)
    return rec


def get_ticket(ticket_id: str) -> dict[str, Any] | None:
    needle = (ticket_id or "").strip().upper()
    for t in _load_all():
        if str(t.get("id", "")).upper() == needle:
            return t
    return None


def list_tickets_for_session(session_id: str) -> list[dict[str, Any]]:
    sid = (session_id or "").strip()
    return [t for t in _load_all() if t.get("session_id") == sid]


def needs_escalation_heuristic(text: str) -> bool:
    """Detección simple por palabras clave (sin llamada al modelo)."""
    s = (text or "").lower()
    if not s.strip():
        return False
    needles = (
        "cobraron dos",
        "cobraron doble",
        "doble cobro",
        "cobro duplicado",
        "me cobraron dos",
        "no puedo entrar",
        "no entro a mi cuenta",
        "no puedo acceder",
        "bloquearon mi cuenta",
        "cuenta bloqueada",
        "hablar con persona",
        "hablar con un humano",
        "asesor humano",
        "operador",
        "agente humano",
        "esto es un robo",
        "fraude",
    )
    return any(n in s for n in needles)
