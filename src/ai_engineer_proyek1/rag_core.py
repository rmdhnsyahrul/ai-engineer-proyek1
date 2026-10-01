import os
import json
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI 
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

load_dotenv()

# 1. Konfigurasi LlamaIndex agar menggunakan OpenRouter (Gratis)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE")

# 2. Menggunakan model embedding bawaan OpenAI (kompatibel dengan OpenRouter)
Settings.embed_model = OpenAIEmbedding(
  model="text-embedding-3-small",
  api_base=OPENROUTER_API_BASE,
  api_key=OPENROUTER_API_KEY
)

# Menggunakan LLM gratisan otomatis dari OpenRouter
Settings.llm = OpenAI(
  model_name="openrouter/free",
  api_base=OPENROUTER_API_BASE,
  api_key=OPENROUTER_API_KEY
)

PERSIST_DIR = os.getenv("PERSIST_DIR", "./storage")

def build_or_load_index():
    """Membaca dokumen mentah, mengubah menjadi vektor, dan menyimpannya ke disk"""
    if os.path.exists(PERSIST_DIR):
        print("-> Memuat Vector Index yang sudah ada dari storage...")
        # 1. Membuat StorageContext dari folder lokal
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    else:
        # Jika belum ada, buat index baru dari dokumen 'data/faq_inaproc.jsonl'
        documents = []
        file_path = 'data/faq_inaproc.jsonl'

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # Satukan pertanyaan dan jawaban sebagai text utama dokumen
                text_content = f"Kategori: {data['category']}\nPertanyaan: {data['question']}\nJawaban: {data['answer']}"

                # Buat objek dokumen LlamaIndex beserta metadata tambahan untuk pelacakan
                doc = Document(
                    text=text_content,
                    metadata={"url": data["url"], "category": data["category"]}
                )
                documents.append(doc)

        index = VectorStoreIndex.from_documents(documents)
        # Simpan ke folder lokal agar tidak perlu hit API berulang kali
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("-> Vector Index berhasil dibuat dan disimpan!")

    return index

if __name__ == "__main__":
    # Test pencarian lokal sederhana
    index = build_or_load_index()
    query_engine = index.as_query_engine()
    
    response = query_engine.query("Mengapa tidak boleh daftar pakai email kantor di INAPROC?")
    print("\n[AI Jawaban]:", response)  