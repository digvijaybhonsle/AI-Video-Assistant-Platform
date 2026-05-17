# rag_engine.py

import os

from typing import List

from dotenv import load_dotenv

from langchain_mistralai import (
    ChatMistralAI
)

from langchain_core.prompts import (
    ChatPromptTemplate
)

from langchain_core.output_parsers import (
    StrOutputParser
)

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever
)

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

# ============================================================
# GLOBAL LLM CACHE
# ============================================================

_llm_cache = {}
RAG_CACHE = {}

# ============================================================
# GET LLM
# ============================================================

def get_llm(
    temperature: float = 0.2
):

    global _llm_cache

    cache_key = str(temperature)

    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    api_key = os.getenv(
        "MISTRAL_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "MISTRAL_API_KEY missing"
        )

    llm = ChatMistralAI(

        model="mistral-small-latest",

        mistral_api_key=api_key,

        temperature=temperature,

        max_tokens=1000,

        timeout=120,
    )

    _llm_cache[cache_key] = llm

    return llm

# ============================================================
# FORMAT DOCUMENTS
# ============================================================

def format_docs(
    docs: List
) -> str:

    formatted = "\n\n".join(

        doc.page_content

        for doc in docs

        if getattr(
            doc,
            "page_content",
            None
        )
    )

    # Prevent huge prompt payloads
    return formatted[:12000]

# ============================================================
# BUILD RAG CHAIN
# ============================================================
def build_rag_chain(

    transcript: str,

    session_id: str
):

    try:
        if session_id in RAG_CACHE:

            print(
                "⚡ Using cached RAG chain"
            )

            return RAG_CACHE[
                session_id
            ]
        print(
            "\n🧠 Building RAG chain..."
        )

        if (
            not transcript
            or
            len(transcript.strip()) < 100
        ):

            raise ValueError(
                "Transcript too short"
            )

        # Prevent memory spikes
        transcript = transcript[:50000]

        # ====================================================
        # VECTOR STORE
        # ====================================================

        vector_store = build_vector_store(
            transcript
        )

        retriever = get_retriever(

            vector_store,

            k=3
        )

        # ====================================================
        # LLM
        # ====================================================

        llm = get_llm(
            temperature=0.2
        )

        # ====================================================
        # PROMPT
        # ====================================================

        prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",

                    """
You are an expert AI meeting assistant.

Answer ONLY using the provided transcript context.

Rules:
- be concise
- be factual
- do not hallucinate
- do not invent details
- cite meeting details naturally

If answer is missing,
reply exactly:
"I could not find this information in the transcript."

Context:
{context}
"""
                ),

                (
                    "human",
                    "{question}"
                ),
            ])
        )

        print(
            "✅ RAG chain ready"
        )

        rag_chain = {

            "retriever": retriever,

            "prompt": prompt,

            "llm": llm,
        }

        # ====================================================
        # CACHE SESSION
        # ====================================================

        RAG_CACHE[
            session_id
        ] = rag_chain

        return rag_chain

    except Exception as e:

        print(
            f"❌ RAG build failed:\n{e}"
        )

        return None
    
# ============================================================
# GET EXISTING RAG
# ============================================================

def get_rag_chain(

    session_id: str
):

    return RAG_CACHE.get(
        session_id
    )

# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(
    rag_chain,
    question: str
) -> str:

    try:

        if not rag_chain:

            return (
                "RAG system is unavailable."
            )

        if (
            not question
            or
            not question.strip()
        ):

            return (
                "Please ask a valid question."
            )

        print(
            f"\n❓ Question:\n{question}"
        )

        retriever = rag_chain[
            "retriever"
        ]

        prompt = rag_chain[
            "prompt"
        ]

        llm = rag_chain[
            "llm"
        ]

        # ====================================================
        # RETRIEVE CONTEXT
        # ====================================================

        docs = retriever.invoke(
            question
        )

        context = format_docs(
            docs
        )

        if not context.strip():

            return (
                "I could not find this "
                "information in the transcript."
            )

        # ====================================================
        # CHAIN
        # ====================================================

        chain = (
            prompt
            | llm
            | StrOutputParser()
        )

        answer = chain.invoke({

            "context": context,

            "question": question
        })

        answer = answer.strip()

        if not answer:

            return (
                "I could not generate "
                "a response."
            )

        print(
            f"✅ Answer generated "
            f"({len(answer)} chars)"
        )

        return answer

    except Exception as e:

        print(
            f"❌ RAG Error:\n{e}"
        )

        return (
            "Sorry, I encountered an "
            "error while processing "
            "your question."
        )