import os
import traceback

from dotenv import load_dotenv

from utils.audio_processor import (
    process_input
)

from core.transcriber import (
    transcribe_all
)

from core.summarizer import (
    summarize,
    generate_title
)

from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)

# OPTIONAL RAG IMPORT
# Delayed for performance
# from backend.core.rag_engine import (
#     build_rag_chain,
#     ask_question
# )

# ========================================================
# LOAD ENVIRONMENT
# ========================================================

load_dotenv()

# ========================================================
# MAIN PIPELINE
# ========================================================

def run_pipeline(
    source,
    language: str = "english"
) -> dict:

    try:

        print("\n" + "=" * 60)
        print("🚀 Starting AI Video Assistant Pipeline")
        print("=" * 60)

        # ====================================================
        # STEP 1 — PROCESS INPUT
        # ====================================================

        print("\n📂 Processing input source...")

        chunks = process_input(source)

        print(
            f"✅ Audio processed successfully "
            f"({len(chunks)} chunk(s))"
        )

        # ====================================================
        # STEP 2 — TRANSCRIPTION
        # ====================================================

        print(
            f"\n🧠 Running Whisper transcription "
            f"({language})..."
        )

        transcript = transcribe_all(
            chunks,
            language
        )

        if not transcript.strip():

            raise Exception(
                "Transcription returned empty result"
            )

        print(
            "\n✅ Transcription completed"
        )

        print(
            f"\n📝 Transcript Preview:\n"
            f"{transcript[:300]}"
        )

        # ====================================================
        # STEP 3 — TITLE GENERATION
        # ====================================================

        print("\n🏷️ Generating title...")

        title = generate_title(
            transcript
        )

        # ====================================================
        # STEP 4 — SUMMARY
        # ====================================================

        print("\n📄 Creating summary...")

        summary = summarize(
            transcript
        )

        # ====================================================
        # STEP 5 — EXTRACTION
        # ====================================================

        print("\n🔍 Extracting insights...")

        action_items = (
            extract_action_items(
                transcript
            )
        )

        decisions = (
            extract_key_decisions(
                transcript
            )
        )

        questions = (
            extract_questions(
                transcript
            )
        )

        # ====================================================
        # OPTIONAL RAG
        # ====================================================

        rag_chain = None

        # Uncomment later if needed
        # print("\n🧠 Building RAG engine...")
        #
        # rag_chain = build_rag_chain(
        #     transcript
        # )

        print(
            "\n🎉 Pipeline completed successfully"
        )

        # ====================================================
        # RETURN RESULTS
        # ====================================================

        return {

            "title": title,

            "transcript": transcript,

            "summary": summary,

            "action_items": action_items,

            "key_decisions": decisions,

            "open_questions": questions,

            "rag_chain": rag_chain,
        }

    except Exception as e:

        print("\n❌ Pipeline Failed")

        traceback.print_exc()

        raise Exception(
            f"Pipeline execution failed: {str(e)}"
        )

# ========================================================
# CLI TEST MODE
# ========================================================

if __name__ == "__main__":

    print("\n🎬 AI Video Assistant\n")

    source = input(
        "Enter local audio/video path: "
    ).strip()

    language = (
        input(
            "Language (english/hinglish): "
        ).strip()
        or "english"
    )

    result = run_pipeline(
        source,
        language
    )

    print("\n" + "=" * 60)

    print(
        f"\n📌 Title:\n{result['title']}"
    )

    print(
        f"\n📋 Summary:\n{result['summary']}"
    )

    print(
        f"\n✅ Action Items:\n"
        f"{result['action_items']}"
    )

    print(
        f"\n🔑 Key Decisions:\n"
        f"{result['key_decisions']}"
    )

    print(
        f"\n❓ Open Questions:\n"
        f"{result['open_questions']}"
    )

    print("\n" + "=" * 60)

    # ====================================================
    # OPTIONAL CHAT MODE
    # ====================================================

    enable_chat = input(
        "\nEnable AI Chat? (y/n): "
    ).strip().lower()

    if enable_chat == "y":

        from backend.core.rag_engine import (
            build_rag_chain,
            ask_question
        )

        print(
            "\n🧠 Initializing RAG engine..."
        )

        rag_chain = build_rag_chain(
            result["transcript"]
        )

        print(
            "\n💬 Chat with your meeting "
            "(type 'exit' to quit)\n"
        )

        while True:

            question = input(
                "You: "
            ).strip()

            if question.lower() in [
                "exit",
                "quit",
                "q"
            ]:

                print("\n👋 Goodbye!")
                break

            if not question:
                continue

            answer = ask_question(
                rag_chain,
                question
            )

            print(
                f"\n🤖 Assistant:\n{answer}\n"
            )