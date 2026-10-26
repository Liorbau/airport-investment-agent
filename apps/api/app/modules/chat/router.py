"""POST /chat streams progress then the checked answer (D-013); POST /speech voices it."""

import logging
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from openai import APIConnectionError, APITimeoutError, OpenAIError, RateLimitError
from pydantic import BaseModel

from app.modules.chat import agent
from app.modules.chat.llm import LlmConfigError, synthesize
from app.modules.chat.schemas import ChatError, ChatRequest, SpeechRequest

router = APIRouter()
logger = logging.getLogger(__name__)

QUOTA_MESSAGE = (
    "The AI provider's usage limit is reached (free tiers allow only a few questions a day). "
    "Try again later, or set another model or provider in apps/api/.env."
)
UNREACHABLE_MESSAGE = "The AI provider can't be reached right now. Please try again in a minute."
UNEXPECTED_MESSAGE = "Something went wrong on our side. Please try again."


def _sse(event: BaseModel) -> str:
    event_as_json = event.model_dump_json()
    return f"data: {event_as_json}\n\n"


def _events(request: ChatRequest) -> Iterator[str]:
    try:
        for event in agent.run(request.history, request.question):
            yield _sse(event)
    except RateLimitError:
        yield _sse(ChatError(message=QUOTA_MESSAGE))
    except (APIConnectionError, APITimeoutError):
        yield _sse(ChatError(message=UNREACHABLE_MESSAGE))
    except LlmConfigError as error:
        yield _sse(ChatError(message=f"The AI provider is not configured: {error}"))
    except OpenAIError as error:
        yield _sse(ChatError(message=f"The AI service failed: {type(error).__name__}"))
    # Last resort at the HTTP edge: the stream has started, so the user must get an event.
    except Exception:
        logger.exception("Chat run failed")
        yield _sse(ChatError(message=UNEXPECTED_MESSAGE))


@router.post("/chat", response_class=StreamingResponse)
def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(_events(request), media_type="text/event-stream")


@router.post("/speech", response_class=Response)
def speech(request: SpeechRequest) -> Response:
    """A natural voice for answers. 501 tells the browser to fall back to its own voice."""
    try:
        audio = synthesize(request.text)
    except OpenAIError as error:
        raise HTTPException(
            status_code=502, detail=f"Voice failed: {type(error).__name__}"
        ) from error
    if audio is None:
        raise HTTPException(status_code=501, detail="Voice needs the OpenAI provider")
    return Response(content=audio, media_type="audio/mpeg")
