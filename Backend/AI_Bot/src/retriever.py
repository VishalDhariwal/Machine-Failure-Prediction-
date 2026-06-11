from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from Backend.AI_Bot.src.ingestion import create_vector_store
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_PATH = (
    BASE_DIR /
    "data" /
    "vector_store"
)

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

retriever = None


def get_retriever():

    global retriever

    if retriever is not None:
        return retriever

    faiss_file = Path(VECTOR_PATH) / "index.faiss"

    if not faiss_file.exists():

        print(
            "[INFO] Vector store not found. Creating..."
        )

        create_vector_store()

    vectorstore = FAISS.load_local(
        str(VECTOR_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return retriever


def retrieve(query: str):

    docs = get_retriever().invoke(query)

    return docs