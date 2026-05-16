# extractor.py
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os


def get_llm(temperature: float = 0.3):
    """Initialize Mistral LLM"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=temperature,
        max_tokens=1500
    )


def build_extraction_chain(system_prompt: str):
    """Reusable chain builder for extraction tasks"""
    llm = get_llm(temperature=0.2)  # Lower temp for structured extraction

    chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )
    return chain


def extract_action_items(transcript: str) -> str:
    """Extract action items"""
    if not transcript or len(transcript.strip()) < 100:
        return "No action items found (transcript too short)."

    prompt = """You are an expert meeting analyst.
    Extract all **action items** from the transcript.

    For each action item, provide:
    - Task description
    - Owner (who is responsible, if mentioned)
    - Deadline (if mentioned, else 'Not specified')

    Format as a clean numbered list.
    If no action items are found, reply with: "No action items found."""

    chain = build_extraction_chain(prompt)
    return chain.invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    """Extract key decisions"""
    if not transcript or len(transcript.strip()) < 100:
        return "No key decisions found (transcript too short)."

    prompt = """You are an expert meeting analyst.
    Extract all **key decisions** made during the meeting.

    For each decision, provide:
    - Decision description
    - Date/time (if mentioned, else 'Not specified')
    - Participants involved (if mentioned, else 'Not specified')

    Format as a clean numbered list.
    If no decisions are found, reply with: "No key decisions found."""

    chain = build_extraction_chain(prompt)
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    """Extract open questions"""
    if not transcript or len(transcript.strip()) < 100:
        return "No questions found (transcript too short)."

    prompt = """You are an expert meeting analyst.
    Extract all **questions** that were raised in the meeting.

    For each question, provide:
    - Question text
    - Who asked it (if mentioned, else 'Not specified')
    - Any answers or discussion points (if mentioned, else 'Not specified')

    Format as a clean numbered list.
    If no questions are found, reply with: "No questions found."""

    chain = build_extraction_chain(prompt)
    return chain.invoke(transcript)