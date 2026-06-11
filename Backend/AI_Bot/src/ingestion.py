from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path

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

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    vectorstore.save_local(str(VECTOR_PATH))

    print("Vector Store Created")


if __name__ == "__main__":
    create_vector_store()