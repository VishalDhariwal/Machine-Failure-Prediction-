import json
import math
import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from Backend.AI_Bot.src.ingestion import create_vector_store

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_PATH = BASE_DIR / "data" / "vector_store"
STORE_FILE = VECTOR_PATH / "store.json"

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
)

store_data = None

def load_store():
    global store_data
    if store_data is not None:
        return
    if not STORE_FILE.exists():
        print("[INFO] Vector store not found. Creating...")
        create_vector_store()
    with open(STORE_FILE, "r") as f:
        store_data = json.load(f)

def cosine_similarity(v1, v2):
    dot = sum(a*b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(b*b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def retrieve(query: str, k: int = 4):
    load_store()
    
    query_vector = embeddings.embed_query(query)
    
    scored = []
    for item in store_data:
        sim = cosine_similarity(query_vector, item["embedding"])
        scored.append((sim, item))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    
    top_items = scored[:k]
    
    docs = []
    for sim, item in top_items:
        docs.append(Document(
            page_content=item["page_content"], 
            metadata=item["metadata"]
        ))
        
    return docs