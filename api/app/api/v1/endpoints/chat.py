import litellm
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
@limiter.limit(settings.CHAT_RATE_LIMIT)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """
    AI chat widget endpoint powered by LiteLLM.
    Rate-limited per IP to prevent abuse.
    """
    messages = [
        {"role": "system", "content": settings.AI_SYSTEM_PROMPT},
        *[m.model_dump() for m in body.messages],
    ]

    response = await litellm.acompletion(
        model=settings.LITELLM_MODEL,
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )

    reply = response.choices[0].message.content or ""
    return ChatResponse(reply=reply)
