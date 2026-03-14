FROM golang:1.24 AS backend-build

ENV CGO_ENABLED=0
ENV GOTOOLCHAIN=local
ENV GOCACHE=/go/pkg/mod

WORKDIR /src

COPY go.mod go.sum ./

RUN --mount=type=cache,target=/go/pkg/mod go mod download

COPY cmd ./cmd
COPY pkg ./pkg

RUN --mount=type=cache,target=/go/pkg/mod \
    go build -ldflags="-s -w" -o /out/slack-mcp-runtime ./cmd/slack-mcp-server

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

COPY pyproject.toml README.md fastmcp.json server.py backend_runtime.py ./
COPY scripts ./scripts

RUN uv sync --no-dev

COPY --from=backend-build /out/slack-mcp-runtime /usr/local/bin/slack-mcp-runtime

EXPOSE 3005

CMD ["/app/.venv/bin/python", "scripts/run_server.py", "serve"]
