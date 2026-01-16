from fastapi import FastAPI
from .router_openai_compat import router as openai_router

app = FastAPI(title="ModelGate", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True, "service": "ModelGate"}

app.include_router(openai_router)
