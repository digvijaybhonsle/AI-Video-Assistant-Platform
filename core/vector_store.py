import os

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ============================================================
# Constants
# ============================================================

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================
# Embedding Model
# ============================================================

def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )


# ============================================================
# Build Vector Store
# ============================================================

def build_vector_store(transcript: str) -> Chroma:

    print("Building Vector Store...")

    # --------------------------------------------------------
    # Validate transcript
    # --------------------------------------------------------

    if transcript is None:
        raise ValueError("Transcript is None.")

    transcript = transcript.strip()

    if len(transcript) == 0:
        raise ValueError("Transcript is empty.")

    # --------------------------------------------------------
    # Split transcript
    # --------------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    # --------------------------------------------------------
    # Remove empty chunks
    # --------------------------------------------------------

    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    if len(chunks) == 0:
        raise ValueError("No valid text chunks generated.")

    print(f"Generated {len(chunks)} chunks.")

    # --------------------------------------------------------
    # Convert to Documents
    # --------------------------------------------------------

    docs = [
        Document(
            page_content=chunk,
            metadata={"chunk_index": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    if len(docs) == 0:
        raise ValueError("No documents created.")

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embeddings = get_embeddings()

    # --------------------------------------------------------
    # Create ChromaDB
    # --------------------------------------------------------

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    print("Vector Store Created Successfully.")

    return vector_store


# ============================================================
# Load Existing Vector Store
# ============================================================

def load_vector_store() -> Chroma:

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store


# ============================================================
# Retriever
# ============================================================

def get_retriever(vector_store: Chroma, k: int = 4):

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )