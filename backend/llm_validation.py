import ipaddress
import socket
from urllib.parse import urlparse

import requests

PRIVATE_HOST_SUFFIXES = (".local", ".internal", ".home", ".lan")
PRIVATE_HOSTNAMES = {"localhost", "metadata.google.internal"}
BLOCKED_PATH_SUFFIXES = (
    "/chat/completions",
    "/completions",
    "/responses",
    "/models",
)


class LlmValidationError(Exception):
    pass


def _normalize_base_url(api_base: str) -> str:
    value = (api_base or "").strip()
    if not value:
        raise LlmValidationError("请填写 Base URL")

    parsed = urlparse(value)
    if parsed.scheme != "https":
        raise LlmValidationError("仅支持 HTTPS Base URL")
    if not parsed.hostname:
        raise LlmValidationError("Base URL 缺少主机名")
    if parsed.query or parsed.fragment:
        raise LlmValidationError("Base URL 不能包含 query 或 fragment")

    path = parsed.path.rstrip("/")
    lowered_host = parsed.hostname.lower()
    if path.lower().endswith(BLOCKED_PATH_SUFFIXES):
        raise LlmValidationError("请填写服务根地址，不要填写具体接口路径")
    if lowered_host in PRIVATE_HOSTNAMES or lowered_host.endswith(PRIVATE_HOST_SUFFIXES):
        raise LlmValidationError("不允许使用本地或内网地址")

    _assert_public_host(lowered_host)

    normalized = f"https://{parsed.netloc}{path}" if path else f"https://{parsed.netloc}"
    return normalized


def _assert_public_host(hostname: str):
    try:
        ip = ipaddress.ip_address(hostname)
        _assert_public_ip(ip)
        return
    except ValueError:
        pass

    try:
        _, _, ips = socket.gethostbyname_ex(hostname)
    except socket.gaierror as exc:
        raise LlmValidationError("Base URL 主机名无法解析") from exc

    if not ips:
        raise LlmValidationError("Base URL 主机名无法解析")

    for raw_ip in ips:
        _assert_public_ip(ipaddress.ip_address(raw_ip))


def _assert_public_ip(ip: ipaddress._BaseAddress):
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise LlmValidationError("不允许使用本地或内网地址")


def validate_openai_compatible_config(api_base: str, api_key: str, model: str) -> dict:
    normalized_base = _normalize_base_url(api_base)
    api_key = (api_key or "").strip()
    model = (model or "").strip()

    if not api_key:
        raise LlmValidationError("请填写 API Key")
    if not model:
        raise LlmValidationError("请填写模型名称")

    try:
        response = requests.get(
            f"{normalized_base}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=(3, 8),
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise LlmValidationError("连接失败，请检查 Base URL 是否可访问") from exc

    if 300 <= response.status_code < 400:
        raise LlmValidationError("服务返回了重定向，已拒绝此次检测")
    if response.status_code in {401, 403}:
        raise LlmValidationError("鉴权失败，请检查 API Key")
    if response.status_code >= 500:
        raise LlmValidationError("服务暂时不可用，请稍后再试")
    if response.status_code >= 400:
        raise LlmValidationError("连接失败，请检查 Base URL、API Key 和模型名称")

    resolved_model = model
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        models = payload.get("data")
        if isinstance(models, list) and models:
            model_ids = [item.get("id") for item in models if isinstance(item, dict) and item.get("id")]
            if model_ids and model not in model_ids:
                return {
                    "ok": True,
                    "message": "连接成功，但服务端未返回该模型，请继续以实际调用为准",
                    "resolved_model": model,
                    "api_base": normalized_base,
                }
            if model_ids:
                resolved_model = model

    return {
        "ok": True,
        "message": "连接成功",
        "resolved_model": resolved_model,
        "api_base": normalized_base,
    }
