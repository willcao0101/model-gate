# ModelGate

ModelGate is a lightweight **OpenAI-compatible gateway** that routes requests to either:

* **Local Ollama** (privacy-first, self-hosted), or
* **OpenAI** (optional, cloud quality)

It is designed to be shared by browser translation tools (e.g., FluentRead) and future projects like **FileManager**.

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
  .env.example
```

## Requirements

* Python 3.10+
* (Optional) Ollama running on a reachable host (e.g. Mac mini)
* (Optional) OpenAI API key (if you want to route to OpenAI)

## Setup

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

Example `.env` for remote Ollama:

```env
MODELGATE_TOKEN=change-me
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://192.168.193.110:11434/v1
TIMEOUT_SECONDS=120
```

## Run

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
