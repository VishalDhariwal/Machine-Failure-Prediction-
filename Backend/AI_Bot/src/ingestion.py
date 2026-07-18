
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os
import json

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR /
    "data" /
    "manuals" /
    "cnc_rag_massive_grounding_manual.pdf"
)

VECTOR_PATH = (
    BASE_DIR /
    "data" /
    "vector_store"
)

def create_vector_store():
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    )
    
    texts = [c.page_content for c in chunks]
    vectors = embeddings.embed_documents(texts)
    
    store_data = []
    for chunk, vector in zip(chunks, vectors):
        store_data.append({
            "page_content": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": vector
        })
        
    VECTOR_PATH.mkdir(parents=True, exist_ok=True)
    with open(VECTOR_PATH / "store.json", "w") as f:
        json.dump(store_data, f)
        
    print("Vector Store Created")

if __name__ == "__main__":
    create_vector_store()