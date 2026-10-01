import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import AsyncOpenAI
# Import fungsi pembuat indeks dari modul RAG yang Anda buat kemarin
from ai_engineer_proyek1.rag_core import build_or_load_index
import asyncio

load_dotenv()

app = FastAPI(title="INAPROC AI Assistant API")

# 1. Inisialisasi Vector Index saat server pertama kali menyala
# Ini memuat database ./storage ke memori agar pencarian nanti sangat cepat
print("-> Menginisialisasi Database Vektor INAPROC...")
index = build_or_load_index()
# Mengubah indeks menjadi mode Chat Engine yang mendukung riwayat percakapan kontekstual
chat_engine = index.as_chat_engine(chat_mode="condense_plus_context")

@app.get("/")
async def root():
    return {"status": "online", "message": "API RAG INAPROC Siap Melayani!"}

@app.get("/chat/inaproc")
async def chat_inaproc(prompt: str):
    """
    Endpoint RAG: Mencari konteks di database FAQ INAPROC,
    lalu mengirimkan jawaban dari LLM secara streaming (SSE).
    """
    
    async def event_generator():
        # Memanggil chat engine LlamaIndex dengan fitur streaming
        # LlamaIndex otomatis mencari dokumen terdekat dan mengirimkannya ke OpenRouter
        response_stream = chat_engine.stream_chat(prompt)
        
        # Mengalirkan token/kata demi kata yang dihasilkan oleh AI
        for token in response_stream.response_gen:
            yield f"data: {token}\n\n"

            # Berikan jeda mikro (yield control) agar FastAPI bisa langsung menyemburkannya ke jaringan
            await asyncio.sleep(0.001)
        
        # Sinyal akhir bahwa AI sudah selesai menjawab
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
