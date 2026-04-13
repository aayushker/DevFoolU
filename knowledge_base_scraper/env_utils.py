"""Helpers for loading environment variables in standalone scripts."""

import os
from pathlib import Path


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def get_env_value(key: str) -> str:
    value = os.getenv(key, "").strip()
    if value:
        return value

    project_root = Path(__file__).resolve().parents[1]
    env_candidates = (
        project_root / ".env",
        project_root / "backend" / ".env",
    )

    for env_path in env_candidates:
        file_values = _read_env_file(env_path)
        if key in file_values and file_values[key]:
            return file_values[key]

    return ""


def require_env_value(key: str) -> str:
    value = get_env_value(key)
    if value:
        return value

    raise RuntimeError(
        f"Missing required environment variable: {key}. "
        "Set it in backend/.env or export it in your shell."
    )