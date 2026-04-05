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
    """Detección simple por palabras clave (sin llamada al modelo). Casos de atención humana / quejas."""
    s = (text or "").lower()
    if not s.strip():
        return False
    needles = (
        "cobraron dos",
        "cobraron doble",
        "doble cobro",
        "cobro duplicado",
        "me cobraron",
        "cobro indebido",
        "cobro extra",
        "cargo no reconocido",
        "no puedo entrar",
        "no entro a mi cuenta",
        "no puedo acceder",
        "bloquearon mi cuenta",
        "cuenta bloqueada",
        "hablar con persona",
        "hablar con un humano",
        "hablar con alguien",
        "ponerme con",
        "comunicarme con un",
        "asesor humano",
        "operador",
        "agente humano",
        "atención humana",
        "atencion humana",
        "esto es un robo",
        "fraude",
        "estafa",
        "me estafaron",
        "queja",
        "reclamo",
        "reclamación",
        "reclamacion",
        "mal servicio",
        "pesimo servicio",
        "pésimo servicio",
        "defectuoso",
        "defectuosa",
        "dañado",
        "danado",
        "roto",
        "no me llegó",
        "no me llego",
        "no llegó mi pedido",
        "no llego mi pedido",
        "pedido equivocado",
        "envío incorrecto",
        "envio incorrecto",
        "paquete perdido",
        "supervisor",
        "gerente",
        "gerencia",
        "indemnización",
        "indemnizacion",
        "abuso",
        "demanda",
        "abogado",
        "no responden",
        "nadie me contesta",
        "sin respuesta",
        "necesito ayuda urgente",
        "ayuda urgente",
        "muy urgente",
        "cancelar mi cuenta",
        "quiero cancelar",
        "devolución rechazada",
        "devolucion rechazada",
        "no me quieren devolver",
        "mal estado",
        "producto vencido",
        "error en el cobro",
        "error en mi pedido",
        "muy molesto",
        "muy molesta",
        "indignado",
        "indignada",
        "terrible experiencia",
        "inaceptable",
    )
    return any(n in s for n in needles)


def is_trivial_repl_greeting(text: str) -> bool:
    """Saludos o cierres muy cortos que no deben abrir ticket en modo escalate."""
    t = (text or "").strip().lower()
    if len(t) < 2:
        return True
    greetings = {
        "hola",
        "hi",
        "hey",
        "buenos días",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "gracias",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "vale",
        "sí",
        "si",
        "no",
        "bye",
        "adiós",
        "adios",
        "chao",
        "salir",
        "exit",
        "quit",
    }
    return t in greetings


def is_followup_ticket_question_only(text: str) -> bool:
    """
    True si el mensaje parece solo una consulta por folio/ticket, sin nueva queja.
    Evita crear un ticket duplicado al preguntar «¿cuál es mi número de ticket?».
    """
    if needs_escalation_heuristic(text):
        return False
    s = (text or "").lower()
    mentions_ref = any(
        w in s
        for w in (
            "ticket",
            "folio",
            "número de caso",
            "numero de caso",
            "número del caso",
            "numero del caso",
            "referencia",
        )
    )
    asks = any(
        w in s
        for w in (
            "cuál",
            "cual",
            "qué",
            "que ",
            "dónde",
            "donde",
            "dame ",
            "dime ",
            "pasame",
            "pásame",
            "necesito el",
            "necesito mi",
            "saber el",
            "saber mi",
            "mostrar",
        )
    )
    return mentions_ref and asks
