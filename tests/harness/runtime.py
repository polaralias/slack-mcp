from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_SERVER = REPO_ROOT / "scripts" / "run_server.py"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PATH = "/mcp"
DEFAULT_HEALTH_PATH = "/health"


class HarnessPrerequisiteError(RuntimeError):
    """Raised when the live Slack-backed harness cannot run in this environment."""


@dataclass(frozen=True)
class DoctorSnapshot:
    returncode: int
    raw_output: str
    fields: dict[str, str]


def _pick_unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((DEFAULT_HOST, 0))
        return int(sock.getsockname()[1])


def _parse_key_value_lines(raw_output: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in raw_output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def _healthcheck(url: str, timeout_seconds: float = 2.0) -> tuple[int | None, str]:
    request = Request(url, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            return getattr(response, "status", None), body
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body
    except URLError as exc:
        raise HarnessPrerequisiteError(f"Health check failed for {url}: {exc}") from exc


class HarnessRuntime:
    def __init__(
        self,
        *,
        enabled_tools: str = "all",
        api_key_mode: str = "disabled",
        enable_harness_upload_tool: bool = False,
        enable_harness_saved_tool: bool = False,
        host: str = DEFAULT_HOST,
        path: str = DEFAULT_PATH,
        health_path: str = DEFAULT_HEALTH_PATH,
    ) -> None:
        self.host = host
        self.port = _pick_unused_port()
        self.path = path
        self.health_path = health_path
        self.enabled_tools = enabled_tools
        self.api_key_mode = api_key_mode
        self.enable_harness_upload_tool = enable_harness_upload_tool
        self.enable_harness_saved_tool = enable_harness_saved_tool
        self.process: subprocess.Popen[str] | None = None
        self.doctor_snapshot: DoctorSnapshot | None = None

    @property
    def mcp_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"

    @property
    def health_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.health_path}"

    def _base_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "SLACK_MCP_ENABLED_TOOLS": self.enabled_tools,
                "SLACK_MCP_HARNESS_UPLOAD_TOOL": "1" if self.enable_harness_upload_tool else "0",
                "SLACK_MCP_HARNESS_SAVED_TOOL": "1" if self.enable_harness_saved_tool else "0",
                "API_KEY_MODE": self.api_key_mode,
                "SLACK_MCP_HOST": self.host,
                "SLACK_MCP_PORT": str(self.port),
                "SLACK_MCP_PATH": self.path,
                "MCP_HOST": self.host,
                "MCP_PORT": str(self.port),
                "MCP_PATH": self.path,
                "MCP_HEALTH_PATH": self.health_path,
                "HOST": self.host,
                "PORT": str(self.port),
                "FASTMCP_TRANSPORT": "streamable-http",
                "MCP_TRANSPORT": "streamable-http",
                "PYTHONUNBUFFERED": "1",
            }
        )
        return env

    def capture_doctor(self) -> DoctorSnapshot:
        completed = subprocess.run(
            [sys.executable, str(RUN_SERVER), "doctor"],
            cwd=REPO_ROOT,
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        raw_output = completed.stdout.strip()
        if completed.stderr:
            raw_output = f"{raw_output}\nSTDERR:\n{completed.stderr.strip()}".strip()
        snapshot = DoctorSnapshot(
            returncode=completed.returncode,
            raw_output=raw_output,
            fields=_parse_key_value_lines(completed.stdout),
        )
        self.doctor_snapshot = snapshot
        return snapshot

    def start(self, startup_timeout_seconds: float = 90.0) -> "HarnessRuntime":
        snapshot = self.capture_doctor()
        if snapshot.returncode != 0:
            raise HarnessPrerequisiteError(
                "Harness prerequisites are not satisfied.\n"
                f"Doctor output:\n{snapshot.raw_output}"
            )

        self.process = subprocess.Popen(
            [sys.executable, str(RUN_SERVER), "serve"],
            cwd=REPO_ROOT,
            env=self._base_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        deadline = time.time() + startup_timeout_seconds
        last_error: str | None = None
        while time.time() < deadline:
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate(timeout=5)
                raise HarnessPrerequisiteError(
                    "Harness server exited before becoming healthy.\n"
                    f"Doctor output:\n{snapshot.raw_output}\n\n"
                    f"STDOUT:\n{stdout.strip()}\n\nSTDERR:\n{stderr.strip()}"
                )
            try:
                status_code, _body = _healthcheck(self.health_url, timeout_seconds=2.0)
                if status_code and 200 <= status_code < 300:
                    return self
                last_error = f"unexpected status {status_code}"
            except HarnessPrerequisiteError as exc:
                last_error = str(exc)
            time.sleep(1.0)

        self.stop()
        raise HarnessPrerequisiteError(
            "Harness server did not become healthy before timeout.\n"
            f"Doctor output:\n{snapshot.raw_output}\n\n"
            f"Last health error: {last_error or 'unknown'}"
        )

    def stop(self) -> None:
        if self.process is None:
            return
        process = self.process
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                else:
                    process.kill()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        for stream_name in ("stdout", "stderr"):
            stream = getattr(process, stream_name, None)
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
        self.process = None

    def health_payload(self) -> dict[str, Any]:
        _status_code, body = _healthcheck(self.health_url, timeout_seconds=5.0)
        import json

        return json.loads(body)
