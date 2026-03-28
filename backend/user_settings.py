import sqlite3
from datetime import datetime

from backend.config import settings


def build_effective_llm_config(user_id: str) -> dict:
    record = get_user_llm_settings_record(user_id) or {}
    api_base = (record.get("api_base") or settings.api_base or "").strip()
    api_key = (record.get("api_key") or settings.api_key or "").strip()
    model = (record.get("model") or settings.model or "").strip()
    return {
        "api_base": api_base,
        "api_key": api_key,
        "model": model,
        "temperature": settings.temperature,
    }


def get_effective_llm_config(user_id: str) -> dict:
    return build_effective_llm_config(user_id)




TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_llm_settings (
    user_id TEXT PRIMARY KEY,
    api_base TEXT NOT NULL DEFAULT '',
    api_key TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def _get_conn() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_user_llm_settings_table():
    conn = _get_conn()
    conn.execute(TABLE_SQL)
    conn.commit()
    conn.close()


def mask_api_key(api_key: str) -> str | None:
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:2]}****{api_key[-4:]}"


def get_user_llm_settings(user_id: str) -> dict:
    conn = _get_conn()
    row = conn.execute(
        "SELECT api_base, api_key, model, updated_at FROM user_llm_settings WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    if not row:
        return {
            "api_base": "",
            "model": "",
            "has_api_key": False,
            "masked_api_key": None,
            "updated_at": None,
        }

    api_key = row["api_key"] or ""
    return {
        "api_base": row["api_base"] or "",
        "model": row["model"] or "",
        "has_api_key": bool(api_key),
        "masked_api_key": mask_api_key(api_key),
        "updated_at": row["updated_at"],
    }


def save_user_llm_settings(user_id: str, api_base: str, model: str, api_key: str | None, replace_api_key: bool) -> dict:
    current = get_user_llm_settings_record(user_id)
    next_api_key = current["api_key"] if current else ""
    if replace_api_key:
        next_api_key = api_key or ""

    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO user_llm_settings (user_id, api_base, api_key, model, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            api_base = excluded.api_base,
            api_key = excluded.api_key,
            model = excluded.model,
            updated_at = excluded.updated_at
        """,
        (user_id, api_base, next_api_key, model, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return get_user_llm_settings(user_id)


def get_user_llm_settings_record(user_id: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT user_id, api_base, api_key, model, updated_at FROM user_llm_settings WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
