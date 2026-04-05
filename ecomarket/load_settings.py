from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]


def default_settings_path() -> Path:
    return Path(__file__).resolve().parent.parent / "settings-final.toml"


def load_settings(toml_path: Path | None = None) -> dict[str, Any]:
    path = toml_path or default_settings_path()
    with path.open("rb") as f:
        return tomllib.load(f)
