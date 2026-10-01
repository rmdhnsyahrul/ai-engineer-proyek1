import os
import json
import logging
from collections.abc import AsyncGenerator
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

logger = logging.getLogger(__name__)
  
client = AsyncOpenAI(
	api_key=os.getenv("OPENROUTER_API_KEY"),
	base_url="https://openrouter.ai/api/v1",
)

class Chat(BaseModel):
  message: str

def format_sse(
	data: dict,
	event: str | None = None,
) -> str:
	"""
	Format a dictionary as a Server-Sent Event.

	Example:
		event: message
		data: {"content": "Hello"}

	"""
	message = ""

	if event:
		message += f"event: {event}\n"

	message += f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

	return message


async def stream_chat(
  prompt: str,
) -> AsyncGenerator[str, None]:
	"""
	Stream chat completion chunks and convert them to SSE messages.
	"""

	try:
		response = await client.chat.completions.create(
			model="openrouter/free",
			messages=[
				{
					"role": "system",
					"content": (
						"Anda adalah asisten AI yang ahli, "
						"singkat, dan jelas."
					),
				},
				{
					"role": "user",
					"content": prompt,
				},
			],
			stream=True,
		)

		async for chunk in response:
			if not chunk.choices:
				continue

			delta = chunk.choices[0].delta

			# Ignore reasoning tokens.
			#
			# Your provider currently sends reasoning separately:
			# delta.reasoning = "..."
			#
			# while actual answer appears in:
			# delta.content = "..."
			content = delta.content

			if content:
				yield format_sse(
					{
							"content": content,
					},
					event="message",
				)

			# The final chunk may contain finish_reason.
			finish_reason = chunk.choices[0].finish_reason

			if finish_reason:
				yield format_sse(
					{
							"finish_reason": finish_reason,
					},
					event="done",
				)

	except Exception as exc:
		logger.exception("Error while streaming chat completion")

		yield format_sse(
			{
				"error": str(exc),
			},
			event="error",
		)

@app.get("/")
async def root():
  # Mengenbalikan JSON otoamtis
  return {"status": "online", "message": "Backend API siap!"}

@app.post("/predict")
async def predict_prompt(prompt: Chat):
  return {
    "user_prompt": prompt.message,
    "ai_response": f"Anda mengirim prompt `{prompt.message}`. Backend Python berhasil memprosesnya."
  }

@app.post("/chat/stream")
async def chat_stream(prompt: Chat):
    return StreamingResponse(
			stream_chat(prompt.message),
			media_type="text/event-stream",
			headers={
				"Cache-Control": "no-cache",
				"Connection": "keep-alive",
				"X-Accel-Buffering": "no",
			},
    )