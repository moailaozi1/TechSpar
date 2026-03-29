from pathlib import Path
import re

from backend.config import settings


ENV_KEYS = ("API_BASE", "API_KEY", "MODEL")
LINE_PATTERN = re.compile(r"^(\s*)([A-Z0-9_]+)\s*=\s*(.*)$")


def get_env_file_path() -> Path:
    return settings.base_dir / ".env"


def mask_api_key(api_key: str) -> str | None:
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:2]}****{api_key[-4:]}"


def _read_env_llm_values() -> dict:
    env_path = get_env_file_path()
    values = {
        "API_BASE": (settings.api_base or "").strip(),
        "API_KEY": (settings.api_key or "").strip(),
        "MODEL": (settings.model or "").strip(),
    }

    if not env_path.exists():
        return values

    for line in env_path.read_text(encoding="utf-8").splitlines():
        match = LINE_PATTERN.match(line)
        if not match:
            continue
        key = match.group(2)
        if key in values:
            values[key] = match.group(3).strip()
    return values


def read_global_llm_settings() -> dict:
    values = _read_env_llm_values()
    api_key = values["API_KEY"]
    return {
        "api_base": values["API_BASE"],
        "model": values["MODEL"],
        "has_api_key": bool(api_key),
        "masked_api_key": mask_api_key(api_key),
    }


def write_global_llm_settings(api_base: str, model: str, api_key: str | None, replace_api_key: bool) -> dict:
    env_path = get_env_file_path()
    original = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = original.splitlines()

    replacements = {
        "API_BASE": api_base,
        "MODEL": model,
    }
    if replace_api_key:
        replacements["API_KEY"] = api_key or ""

    seen = set()
    updated_lines = []
    for line in lines:
        match = LINE_PATTERN.match(line)
        if not match:
            updated_lines.append(line)
            continue

        indent, key = match.group(1), match.group(2)
        if key in replacements:
            updated_lines.append(f"{indent}{key}={replacements[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)

    for key in ENV_KEYS:
        if key in replacements and key not in seen:
            updated_lines.append(f"{key}={replacements[key]}")

    updated_content = "\n".join(updated_lines).rstrip() + "\n"
    if updated_content != original:
        env_path.write_text(updated_content, encoding="utf-8")
    return read_global_llm_settings()
