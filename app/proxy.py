import json
import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse
from .settings import settings
from fastapi.responses import JSONResponse


def choose_provider_from_model(model: str | None) -> str:
    """
    Route rule:
      - model startswith 'ollama/' -> ollama
      - else -> default_provider (openai)
    """
    if model and model.lower().startswith("ollama/"):
        return "ollama"
    return settings.default_provider.lower()

def upstream_base_and_headers(provider: str) -> tuple[str, dict]:
    if provider == "ollama":
        return settings.ollama_base_url, {}
    # openai
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set but provider=openai")
    return settings.openai_base_url, {"Authorization": f"Bearer {settings.openai_api_key}"}

def normalize_model_for_ollama(model: str | None) -> str | None:
    # Convert "ollama/qwen2.5:7b" -> "qwen2.5:7b"
    if not model:
        return model
    if model.lower().startswith("ollama/"):
        return model.split("/", 1)[1]
    return model

async def proxy_openai_compat_post(request: Request, path: str) -> Response:
    body = await request.body()
    body_json = {}
    try:
        body_json = json.loads(body.decode("utf-8")) if body else {}
    except Exception:
        body_json = {}

    model = body_json.get("model")
    provider = choose_provider_from_model(model)

    base_url, upstream_headers = upstream_base_and_headers(provider)
    url = f"{base_url}{path}"

    # If going to ollama, strip "ollama/" prefix
    if provider == "ollama" and isinstance(body_json, dict):
        body_json["model"] = normalize_model_for_ollama(model)
        body = json.dumps(body_json).encode("utf-8")

    is_stream = bool(body_json.get("stream", False))
    timeout = httpx.Timeout(settings.timeout_seconds)

    headers = {"Content-Type": request.headers.get("Content-Type", "application/json")}
    headers.update(upstream_headers)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if is_stream:
                async def gen():
                    async with client.stream("POST", url, headers=headers, content=body) as r:
                        async for chunk in r.aiter_bytes():
                            yield chunk

                return StreamingResponse(gen(), media_type="text/event-stream")

            r = await client.post(url, headers=headers, content=body)
            return Response(content=r.content, status_code=r.status_code,
                            media_type=r.headers.get("Content-Type", "application/json"))

    except httpx.ConnectError as e:
        return JSONResponse(status_code=502, content={
            "error": {"type": "upstream_connect_error", "message": f"Upstream connect failed: {e}"}
        })
    except httpx.ReadTimeout:
        return JSONResponse(status_code=504, content={
            "error": {"type": "upstream_timeout", "message": "Upstream timeout"}
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": {"type": "modelgate_error", "message": f"ModelGate internal error: {e}"}
        })

