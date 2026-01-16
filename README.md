# ModelGate

ModelGate is a lightweight **OpenAI-compatible gateway** that routes requests to either:

* **Local Ollama** (privacy-first, self-hosted), or
* **OpenAI** (optional, cloud quality)

It is designed to be shared by browser translation tools (e.g., FluentRead) and future projects like **FileManager**.

---

## Features

* OpenAI-compatible endpoints:

  * `POST /v1/chat/completions`
  * `POST /v1/embeddings`
* Simple gateway authentication (`Authorization: Bearer <MODELGATE_TOKEN>`)
* Provider routing:

  * Default provider via `DEFAULT_PROVIDER`
  * Force Ollama by using `model: "ollama/<model-name>"` (e.g. `ollama/qwen2.5:3b`)
* Streaming passthrough (`stream: true`)
* Clear upstream error mapping (502/504) (if enabled in `proxy.py`)

---

## Project Structure

```
ModelGate/
  app/
    main.py
    settings.py
    auth.py
    router_openai_compat.py
    proxy.py
  tests/
  Dockerfile
  docker-compose.yml
  .dockerignore
  .env.example
  requirements.txt
  README.md
```

---

## Requirements

### Local development

* Python 3.10+
* (Optional) Ollama running on a reachable host (e.g., a home server / NAS / desktop)
* (Optional) OpenAI API key (if you want to route to OpenAI)

### Deployment (recommended)

* Docker + Docker Compose

---

## Setup (Local Dev)

### 1) Create venv and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don't have `requirements.txt`, install:

```bash
pip install fastapi uvicorn[standard] httpx pydantic-settings python-dotenv
```

### 2) Configure environment variables

Copy `.env.example` to `.env` and edit values:

```bash
cp .env.example .env
```

Example `.env` for a remote Ollama host:

```env
MODELGATE_TOKEN=change-me
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://<OLLAMA_HOST_IP>:11434/v1
TIMEOUT_SECONDS=120
```

Optional OpenAI settings:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## Run (Local Dev)

```bash
uvicorn app.main:app --reload --port 8010
```

Health check:

```bash
curl http://127.0.0.1:8010/health
```

Chat completion example:

```bash
curl -s http://127.0.0.1:8010/v1/chat/completions \
  -H "Authorization: Bearer change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"qwen2.5:3b",
    "messages":[{"role":"user","content":"Translate to Chinese: Good morning."}]
  }'
```

Force Ollama routing (even if default provider is OpenAI):

```bash
curl -s http://127.0.0.1:8010/v1/chat/completions \
  -H "Authorization: Bearer change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"ollama/qwen2.5:3b",
    "messages":[{"role":"user","content":"Translate to Chinese: Good morning."}]
  }'
```

---

## Deployment (Docker Compose, Recommended)

This setup runs:

* **Ollama** on a host machine (self-hosted)
* **ModelGate** in Docker Compose (auto-restart)

### 1) Ensure Ollama is running

Verify Ollama from the Ollama host:

```bash
curl -s http://127.0.0.1:11434/api/tags
```

Or from another machine on the same network:

```bash
curl -s http://<OLLAMA_HOST_IP>:11434/api/tags
```

> If you want Ollama to be reachable from other machines, make sure it listens on a non-loopback address (e.g., `0.0.0.0:11434`).

### 2) Run ModelGate with Docker Compose

#### 2.1 Clone the repo on your server

```bash
mkdir -p ~/Services
cd ~/Services
git clone git@github.com:<your-username>/ModelGate.git
cd ModelGate
```

#### 2.2 Create `.env` on the server

```bash
cp .env.example .env
```

**Option A (macOS Docker Desktop):** reach host services via `host.docker.internal`

```env
MODELGATE_TOKEN=change-me
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
TIMEOUT_SECONDS=120
```

**Option B (Linux server / remote Ollama host):** point directly to the Ollama host IP

```env
MODELGATE_TOKEN=change-me
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://<OLLAMA_HOST_IP>:11434/v1
TIMEOUT_SECONDS=120
```

#### 2.3 Start ModelGate

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

View logs:

```bash
docker logs -f modelgate
```

Health check (on the server):

```bash
curl http://127.0.0.1:8010/health
```

### 3) Test from another machine (e.g., laptop)

```bash
curl http://<SERVER_IP>:8010/health
```

Chat completion test:

```bash
curl -s http://<SERVER_IP>:8010/v1/chat/completions \
  -H "Authorization: Bearer <MODELGATE_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"qwen2.5:3b",
    "messages":[{"role":"user","content":"Translate to Chinese: Good morning."}]
  }'
```

---

## Translation Tool Integration (Example)

In your translation tool:

* Base URL: `http://<SERVER_IP>:8010/v1`
* API Key: `<MODELGATE_TOKEN>`
* Model: `qwen2.5:3b` (or `ollama/qwen2.5:3b` to force Ollama routing)

---

## Security Notes

* Do **NOT** commit `.env` to GitHub.
* Keep `MODELGATE_TOKEN` private.
* If you expose ModelGate to the public internet (e.g., tunnel / reverse proxy):

  * Use TLS
  * Add IP allowlist / rate limiting
  * Rotate tokens periodically

---

## Troubleshooting

### Invalid token

* Ensure the request uses:

  * `Authorization: Bearer <MODELGATE_TOKEN>`
* Ensure Docker is loading `.env`:

  ```bash
  docker exec -it modelgate sh -lc 'env | grep MODELGATE_TOKEN || echo "MODELGATE_TOKEN not set"'
  ```
* Restart to apply `.env` changes:

  ```bash
  docker compose down
  docker compose up -d --build
  ```

### Upstream connect error (Ollama not reachable)

* Verify Ollama is reachable:

  ```bash
  curl -s http://<OLLAMA_HOST_IP>:11434/api/tags
  ```
* Verify `OLLAMA_BASE_URL` is correct:

  * macOS Docker Desktop (host Ollama): `http://host.docker.internal:11434/v1`
  * Linux / remote Ollama: `http://<OLLAMA_HOST_IP>:11434/v1`

### Inspect runtime env inside container

```bash
docker exec -it modelgate sh -lc 'env | grep -E "MODELGATE_TOKEN|OLLAMA_BASE_URL|DEFAULT_PROVIDER"'
```

