FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && pip install --no-cache-dir uv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md fastmcp.json server.py backend_runtime.py slack_native.py ./
COPY scripts ./scripts

RUN uv sync --no-dev

EXPOSE 3005

CMD ["/app/.venv/bin/python", "scripts/run_server.py", "serve"]
