from fastapi import APIRouter, Depends, Request
from .auth import require_token
from .proxy import proxy_openai_compat_post

router = APIRouter(prefix="/v1", dependencies=[Depends(require_token)])

@router.post("/chat/completions")
async def chat_completions(request: Request):
    return await proxy_openai_compat_post(request, "/chat/completions")

@router.post("/embeddings")
async def embeddings(request: Request):
    return await proxy_openai_compat_post(request, "/embeddings")
