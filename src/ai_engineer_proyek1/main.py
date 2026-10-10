import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ai_engineer_proyek1.agent_core import run_agent_events

logger = logging.getLogger(__name__)

app = FastAPI(title="CSV Analysis Agent API", version="0.1.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


def format_sse(data: dict[str, Any], event: str | None = None) -> str:
    """Format a dictionary as a Server-Sent Event message."""
    message = f"event: {event}\n" if event else ""
    message += f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    return message


async def stream_agent(prompt: str) -> AsyncGenerator[str, None]:
    """Convert agent progress events into SSE messages."""
    try:
        async for agent_event in run_agent_events(prompt):
            event_type = agent_event["type"]
            event_data = {
                key: value
                for key, value in agent_event.items()
                if key != "type"
            }
            yield format_sse(event_data, event=event_type)
    except Exception as exc:
        logger.exception("Unexpected error while streaming agent events")
        yield format_sse({"error": str(exc)}, event="error")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "online", "message": "CSV analysis agent is ready."}


@app.post("/agent/stream")
async def agent_stream(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_agent(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )