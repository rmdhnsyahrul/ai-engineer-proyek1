import os
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

class Chat(BaseModel):
  message: str

app = FastAPI()

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

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY")
)

@app.post("/chat/stream")
async def chat_stream(prompt: Chat):
  response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-lightning:free",
    messages=[
      {
        "role": "user",
        "content": prompt.message
      }
    ],
    extra_body={"reasoning": {"enabled": True}}
  )

  # Extract assistant message
  response = response.choices[0].message

  return {
    "user_prompt": prompt.message,
    "ai_response": {
      "role": "assistant",
      "content": response.content,
      "reasonings_detail": response.reasoning_details
    }
  }
