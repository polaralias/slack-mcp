from __future__ import annotations

import csv
import os
from io import StringIO
from typing import Any

from tests.harness.normalize import resource_contents_text, tool_result_text


def csv_rows(csv_text: str) -> list[dict[str, str]]:
    cleaned = csv_text.strip()
    if not cleaned:
        return []
    return list(csv.DictReader(StringIO(cleaned)))


async def discover_channels(client: Any) -> list[dict[str, str]]:
    result = await client.call_tool(
        "channels_list",
        {"channel_types": "public_channel,private_channel,im,mpim", "limit": 20},
    )
    return csv_rows(tool_result_text(result))


async def discover_users_resource_rows(client: Any) -> list[dict[str, str]]:
    resources = await client.list_resources()
    users_resource = next((resource for resource in resources if str(resource.uri).endswith("/users")), None)
    if users_resource is None:
        return []
    contents = await client.read_resource(str(users_resource.uri))
    return csv_rows(resource_contents_text(contents))


async def discover_history_rows(client: Any, channel_id: str, limit: str = "20") -> list[dict[str, str]]:
    result = await client.call_tool("conversations_history", {"channel_id": channel_id, "limit": limit})
    return csv_rows(tool_result_text(result))


def choose_history_channel_id(rows: list[dict[str, str]]) -> str | None:
    configured = os.getenv("SLACK_MCP_TEST_PREFERRED_CHANNELS", "#general")
    preferred_names = {name.strip() for name in configured.split(",") if name.strip()}
    for row in rows:
        channel_id = row.get("ID", "")
        name = row.get("Name", "")
        if channel_id.startswith("C") and name in preferred_names:
            return channel_id
    for row in rows:
        channel_id = row.get("ID", "")
        if channel_id.startswith("C"):
            return channel_id
    return None


def choose_thread_ts(rows: list[dict[str, str]]) -> str | None:
    for row in rows:
        thread_ts = (row.get("ThreadTs") or "").strip()
        if thread_ts:
            return thread_ts
    return None


def choose_search_query(rows: list[dict[str, str]]) -> str | None:
    for row in rows:
        text = (row.get("Text") or "").strip()
        if "validation" in text.lower():
            return "validation"
        if text:
            parts = [part for part in text.split() if len(part) >= 4]
            if parts:
                return parts[0]
    return None


def choose_user_query(rows: list[dict[str, str]]) -> str | None:
    for row in rows:
        username = (row.get("UserName") or "").strip()
        if username and username.lower() != "slackbot":
            return username[: min(6, len(username))]
    for row in rows:
        real_name = (row.get("RealName") or "").strip()
        if real_name and real_name.lower() != "slackbot":
            return real_name.split()[0]
    return None
