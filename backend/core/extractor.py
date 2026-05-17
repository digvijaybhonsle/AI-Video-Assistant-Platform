# extractor.py

import os

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

        max_tokens=1200,

        timeout=120,
    )

    _llm_cache[cache_key] = llm

    return llm

# ============================================================
# GENERIC EXTRACTION RUNNER
# ============================================================

def run_extraction(
    transcript: str,
    system_prompt: str,
    fallback: str
) -> str:

    try:

        if (
            not transcript
            or
            len(transcript.strip()) < 100
        ):

            return fallback

        print(
            "\n🔍 Running extraction..."
        )

        # Prevent giant prompt payloads
        transcript = transcript[:15000]

        llm = get_llm(
            temperature=0.2
        )

        prompt = (
            ChatPromptTemplate
            .from_messages([

                (
                    "system",
                    system_prompt
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

        result = chain.invoke({

            "text":
            transcript
        })

        return result.strip()

    except Exception as e:

        print(
            f"❌ Extraction failed:\n{e}"
        )

        return fallback

# ============================================================
# ACTION ITEMS
# ============================================================

def extract_action_items(
    transcript: str
) -> str:

    prompt = """
You are an expert meeting analyst.

Extract all action items.

For each item include:
- Task
- Owner (if mentioned)
- Deadline (if mentioned)

Format:
1.
2.
3.

Be concise and professional.

If none exist,
reply exactly:
No action items found.
"""

    return run_extraction(

        transcript=transcript,

        system_prompt=prompt,

        fallback="No action items found."
    )

# ============================================================
# KEY DECISIONS
# ============================================================

def extract_key_decisions(
    transcript: str
) -> str:

    prompt = """
You are an expert meeting analyst.

Extract all key decisions made.

For each decision include:
- Decision
- Participants involved
- Context (brief)

Format:
1.
2.
3.

Be concise and professional.

If none exist,
reply exactly:
No key decisions found.
"""

    return run_extraction(

        transcript=transcript,

        system_prompt=prompt,

        fallback="No key decisions found."
    )

# ============================================================
# OPEN QUESTIONS
# ============================================================

def extract_questions(
    transcript: str
) -> str:

    prompt = """
You are an expert meeting analyst.

Extract unresolved or open questions.

For each question include:
- Question
- Who asked it (if mentioned)
- Current status

Format:
1.
2.
3.

Be concise and professional.

If none exist,
reply exactly:
No open questions found.
"""

    return run_extraction(

        transcript=transcript,

        system_prompt=prompt,

        fallback="No open questions found."
    )