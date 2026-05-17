# vector_store.py

import os
import shutil
import uuid

from typing import Optional

from langchain_chroma import Chroma

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_core.documents import (
    Document
)

# ============================================================
# CONFIG
# ============================================================

CHROMA_DIR = "chroma_db"

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)

# ============================================================
# GLOBAL EMBEDDING CACHE
# ============================================================

_embeddings = None

# ============================================================
# LOAD EMBEDDINGS
# ============================================================

def get_embeddings():

    global _embeddings

    if _embeddings is None:

        print(
            "\n🧠 Loading embedding model..."
        )

        _embeddings = (
            HuggingFaceEmbeddings(

                model_name=EMBEDDING_MODEL,

                model_kwargs={
                    "device": "cpu"
                },

                encode_kwargs={
                    "normalize_embeddings": True
                }
            )
        )

        print(
            "✅ Embedding model loaded"
        )

    return _embeddings


# ============================================================
# BUILD VECTOR STORE
# ============================================================

def build_vector_store(
    transcript: str
) -> Chroma:

    print(
        "\n📚 Building Vector Store..."
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if transcript is None:

        raise ValueError(
            "Transcript is None."
        )

    transcript = transcript.strip()

    if not transcript:

        raise ValueError(
            "Transcript is empty."
        )

    # Prevent massive memory spikes
    transcript = transcript[:50000]

    # ========================================================
    # SPLITTER
    # ========================================================

    splitter = (
        RecursiveCharacterTextSplitter(

            chunk_size=600,

            chunk_overlap=60,

            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )
    )

    chunks = splitter.split_text(
        transcript
    )

    chunks = [

        chunk.strip()

        for chunk in chunks

        if chunk.strip()
    ]

    if not chunks:

        raise ValueError(
            "No valid chunks created."
        )

    print(
        f"✅ Generated "
        f"{len(chunks)} chunks"
    )

    # ========================================================
    # DOCUMENTS
    # ========================================================

    docs = [

        Document(

            page_content=chunk,

            metadata={
                "chunk_index": i
            }
        )

        for i, chunk in enumerate(
            chunks
        )
    ]

    # ========================================================
    # EMBEDDINGS
    # ========================================================

    embeddings = get_embeddings()

    # ========================================================
    # UNIQUE COLLECTION
    # ========================================================

    collection_name = (
        f"meeting_"
        f"{uuid.uuid4().hex[:8]}"
    )

    # ========================================================
    # VECTOR STORE
    # ========================================================

    vector_store = (
        Chroma.from_documents(

            documents=docs,

            embedding=embeddings,

            collection_name=collection_name,
        )
    )

    print(
        "✅ Vector Store created"
    )

    return vector_store

# ============================================================
# LOAD VECTOR STORE
# ============================================================

def load_vector_store(
    collection_name: str
) -> Optional[Chroma]:

    try:

        embeddings = get_embeddings()

        vector_store = Chroma(

            collection_name=collection_name,

            embedding_function=embeddings,

            persist_directory=CHROMA_DIR
        )

        return vector_store

    except Exception as e:

        print(
            f"❌ Failed to load vector store:\n{e}"
        )

        return None

# ============================================================
# RETRIEVER
# ============================================================

def get_retriever(
    vector_store: Chroma,
    k: int = 3
):

    return vector_store.as_retriever(

        search_type="similarity",

        search_kwargs={
            "k": k
        }
    )