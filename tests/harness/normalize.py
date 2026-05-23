from __future__ import annotations

from typing import Any


def tool_result_is_error(result: Any) -> bool:
    if hasattr(result, "is_error"):
        return bool(getattr(result, "is_error"))
    return bool(getattr(result, "isError", False))


def tool_result_text(result: Any) -> str:
    parts: list[str] = []
    for content in getattr(result, "content", []) or []:
        text = getattr(content, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def tool_result_has_payload(result: Any) -> bool:
    if getattr(result, "structuredContent", None):
        return True
    return bool(tool_result_text(result))


def resource_contents_text(contents: list[Any]) -> str:
    parts: list[str] = []
    for content in contents:
        text = getattr(content, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def resource_contents_have_payload(contents: list[Any]) -> bool:
    if any(getattr(content, "blob", None) for content in contents):
        return True
    return bool(resource_contents_text(contents))
