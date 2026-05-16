# rag_engine.py
import os
from typing import List
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.vector_store import build_vector_store, load_vector_store, get_retriever


def get_llm(temperature: float = 0.3):
    """Initialize Mistral LLM"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=temperature,
        max_tokens=2048
    )


def format_docs(docs: List) -> str:
    """Format retrieved documents for the prompt"""
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(transcript: str):
    """Build fresh RAG chain from transcript"""
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=4)

    llm = get_llm(temperature=0.3)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting/video assistant. 
Answer the user's question **based ONLY** on the provided transcript context.

If the answer cannot be found in the context, respond with:
"I could not find this information in the transcript."

Be concise, accurate, and professional. Mention speakers when relevant.

Context:
{context}"""
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    """Load existing vector store (for future persistent sessions)"""
    vector_store = load_vector_store()
    retriever = get_retriever(vector_store, k=4)

    llm = get_llm(temperature=0.3)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting/video assistant. 
Answer the user's question **based ONLY** on the provided transcript context.

If the answer cannot be found in the context, respond with:
"I could not find this information in the transcript."

Be concise, accurate, and professional.

Context:
{context}"""
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    """Ask a question using the RAG chain"""
    if not question or not question.strip():
        return "Please ask a valid question."

    try:
        print(f"❓ Question: {question}")
        answer = rag_chain.invoke(question)
        print(f"✅ Answer generated ({len(answer)} chars)")
        return answer.strip()
    except Exception as e:
        print(f"❌ RAG Error: {e}")
        return f"Sorry, I encountered an error while processing your question: {str(e)[:100]}"