# summarizer.py
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough

import os
from typing import List


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


def split_transcript(transcript: str, chunk_size: int = 3000, chunk_overlap: int = 200) -> List[str]:
    """Split transcript into manageable chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    """Generate a professional summary of the video transcript"""
    if not transcript or len(transcript.strip()) < 50:
        return "Transcript is too short to generate a meaningful summary."

    llm = get_llm(temperature=0.3)

    # Map prompt - summarize each chunk
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert video content summarizer.
Summarize the following portion of a video transcript concisely and clearly."""),
        ("human", "{text}"),
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    # Split into chunks
    chunks = split_transcript(transcript)

    # Process chunks (you can use batching for better performance)
    chunk_summaries = []
    for chunk in chunks:
        try:
            summary = map_chain.invoke({"text": chunk})
            chunk_summaries.append(summary)
        except Exception as e:
            chunk_summaries.append(f"[Summary failed for this section: {str(e)[:100]}]")

    combined_summaries = "\n\n".join(chunk_summaries)

    # Final combine prompt
    combine_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert video summarizer. 
Create a clean, professional, and well-structured summary of the video content.
Use bullet points and organize the content logically.
Include key points, main ideas, and important takeaways."""),
        ("human", "{text}"),
    ])

    combine_chain = (
        RunnablePassthrough()
        | combine_prompt
        | llm
        | StrOutputParser()
    )

    final_summary = combine_chain.invoke(combined_summaries)
    return final_summary


def generate_title(transcript: str) -> str:
    """Generate a catchy and professional title for the video"""
    if not transcript or len(transcript.strip()) < 100:
        return "Untitled Video"

    llm = get_llm(temperature=0.1)  # Lower temperature for title generation

    title_prompt = ChatPromptTemplate.from_messages([
        ("system", """Generate a short, engaging, and professional title for this video.
Maximum 8-10 words. Return only the title, no explanations."""),
        ("human", "{text}"),
    ])

    title_chain = (
        RunnablePassthrough()
        | title_prompt
        | llm
        | StrOutputParser()
    )

    # Use first part of transcript for title generation
    return title_chain.invoke(transcript[:2500]).strip()


# Optional: Add notes / key points generator
def generate_key_notes(transcript: str) -> str:
    """Generate bullet point key notes from the transcript"""
    llm = get_llm(temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract the most important key points from this video transcript.
Return them as clear, actionable bullet points."""),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain.invoke(transcript[:8000])  # Limit context