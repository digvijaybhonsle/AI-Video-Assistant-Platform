# summarizer.py

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

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

# ============================================================
# GLOBAL LLM CACHE
# ============================================================

_llm_cache = {}

# ============================================================
# LLM INITIALIZER
# ============================================================

def get_llm(
    temperature: float = 0.3
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

        max_tokens=1500,

        timeout=120,
    )

    _llm_cache[cache_key] = llm

    return llm

# ============================================================
# TRANSCRIPT SPLITTER
# ============================================================

def split_transcript(
    transcript: str,
    chunk_size: int = 2000,
    chunk_overlap: int = 150
) -> List[str]:

    splitter = (
        RecursiveCharacterTextSplitter(

            chunk_size=chunk_size,

            chunk_overlap=chunk_overlap,

            length_function=len,

            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )
    )

    return splitter.split_text(
        transcript
    )

# ============================================================
# SUMMARY GENERATION
# ============================================================

def summarize(
    transcript: str
) -> str:

    try:

        if (
            not transcript
            or
            len(transcript.strip()) < 50
        ):

            return (
                "Transcript too short "
                "to summarize."
            )

        print(
            "\n📄 Generating summary..."
        )

        llm = get_llm(
            temperature=0.3
        )

        # ====================================================
        # MAP PROMPT
        # ====================================================

        map_prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",

                    """
You are an expert meeting and video summarizer.

Create a concise summary of the transcript section.

Focus on:
- key ideas
- important discussion points
- conclusions
- context
"""
                ),

                (
                    "human",
                    "{text}"
                ),
            ])
        )

        map_chain = (
            map_prompt
            | llm
            | StrOutputParser()
        )

        # ====================================================
        # SPLIT TRANSCRIPT
        # ====================================================

        chunks = split_transcript(
            transcript
        )

        chunk_summaries = []

        for i, chunk in enumerate(
            chunks
        ):

            print(
                f"📝 Summarizing chunk "
                f"{i+1}/{len(chunks)}"
            )

            try:

                summary = map_chain.invoke({
                    "text": chunk
                })

                chunk_summaries.append(
                    summary
                )

            except Exception as e:

                print(
                    f"❌ Chunk summary failed:\n{e}"
                )

        if not chunk_summaries:

            return (
                "Summary generation failed."
            )

        # ====================================================
        # COMBINE
        # ====================================================

        combined = "\n\n".join(
            chunk_summaries
        )

        # Prevent huge token explosion
        combined = combined[:12000]

        combine_prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",

                    """
Create a final polished meeting summary.

Use:
- bullet points
- concise structure
- professional tone

Include:
- main topics
- key decisions
- important insights
- final outcomes
"""
                ),

                (
                    "human",
                    "{text}"
                ),
            ])
        )

        combine_chain = (
            combine_prompt
            | llm
            | StrOutputParser()
        )

        final_summary = (
            combine_chain.invoke({
                "text": combined
            })
        )

        return final_summary.strip()

    except Exception as e:

        print(
            f"❌ Summary failed:\n{e}"
        )

        return (
            f"Summary generation failed: "
            f"{str(e)}"
        )

# ============================================================
# TITLE GENERATION
# ============================================================

def generate_title(
    transcript: str
) -> str:

    try:

        if (
            not transcript
            or
            len(transcript.strip()) < 100
        ):

            return "Untitled Meeting"

        print(
            "\n🏷️ Generating title..."
        )

        llm = get_llm(
            temperature=0.1
        )

        title_prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",

                    """
Generate a concise professional title.

Rules:
- max 8 words
- clear
- engaging
- no quotes
- no explanation
"""
                ),

                (
                    "human",
                    "{text}"
                ),
            ])
        )

        title_chain = (
            title_prompt
            | llm
            | StrOutputParser()
        )

        title = title_chain.invoke({

            "text":
            transcript[:2500]
        })

        return title.strip()

    except Exception as e:

        print(
            f"❌ Title generation failed:\n{e}"
        )

        return "AI Meeting Analysis"

# ============================================================
# KEY NOTES
# ============================================================

def generate_key_notes(
    transcript: str
) -> str:

    try:

        llm = get_llm(
            temperature=0.2
        )

        prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",

                    """
Extract key actionable notes.

Use concise bullet points.
"""
                ),

                (
                    "human",
                    "{text}"
                ),
            ])
        )

        chain = (
            prompt
            | llm
            | StrOutputParser()
        )

        return chain.invoke({

            "text":
            transcript[:8000]
        })

    except Exception as e:

        return (
            f"Key notes generation failed: "
            f"{str(e)}"
        )