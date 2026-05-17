# transcriber.py

import os
import time
import tempfile
from pathlib import Path
from typing import List

import requests
import whisper

from dotenv import load_dotenv

from pydub import AudioSegment

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "tiny"
)

SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

SARVAM_STT_TRANSLATE_URL = (
    "https://api.sarvam.ai/"
    "speech-to-text-translate"
)

SARVAM_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v2.5"
)

SARVAM_PIECE_SECONDS = 25

_model = None

# ============================================================
# LOAD WHISPER MODEL
# ============================================================

def load_whisper_model():

    global _model

    if _model is None:

        print(
            f"\n🧠 Loading Whisper model: "
            f"{WHISPER_MODEL}"
        )

        start = time.time()

        _model = whisper.load_model(
            WHISPER_MODEL
        )

        print(
            f"✅ Whisper loaded in "
            f"{time.time() - start:.1f}s"
        )

    return _model

# ============================================================
# WHISPER TRANSCRIPTION
# ============================================================

def transcribe_chunk_whisper(
    chunk_path: str
) -> str:

    model = load_whisper_model()

    try:

        result = model.transcribe(

            chunk_path,

            task="transcribe",

            language=None,

            fp16=False,

            condition_on_previous_text=False
        )

        text = result.get(
            "text",
            ""
        ).strip()

        if not text:

            return "[Empty transcription]"

        return text

    except Exception as e:

        print(
            f"❌ Whisper error:\n{e}"
        )

        return (
            f"[Whisper Error: "
            f"{str(e)[:100]}]"
        )

# ============================================================
# SARVAM REQUEST
# ============================================================

def _send_to_sarvam(
    piece_path: str
) -> str:

    if not SARVAM_API_KEY:

        raise RuntimeError(
            "SARVAM_API_KEY missing"
        )

    headers = {

        "api-subscription-key":
        SARVAM_API_KEY
    }

    try:

        with open(
            piece_path,
            "rb"
        ) as f:

            files = {
                "file": (
                    Path(piece_path).name,
                    f,
                    "audio/wav"
                )
            }

            data = {

                "model":
                SARVAM_MODEL,

                "with_diarization":
                "false"
            }

            response = requests.post(

                SARVAM_STT_TRANSLATE_URL,

                headers=headers,

                files=files,

                data=data,

                timeout=(30, 120)
            )

        if not response.ok:

            print(
                f"❌ Sarvam API Error "
                f"{response.status_code}"
            )

            return ""

        return response.json().get(
            "transcript",
            ""
        ).strip()

    except Exception as e:

        print(
            f"❌ Sarvam request failed:\n{e}"
        )

        return ""

# ============================================================
# SARVAM TRANSCRIPTION
# ============================================================

def transcribe_chunk_sarvam(
    chunk_path: str
) -> str:

    audio = AudioSegment.from_wav(
        chunk_path
    )

    piece_ms = (
        SARVAM_PIECE_SECONDS
        * 1000
    )

    full_text = []

    total_pieces = (
        len(audio)
        + piece_ms
        - 1
    ) // piece_ms

    for i, start in enumerate(

        range(
            0,
            len(audio),
            piece_ms
        )
    ):

        piece = audio[
            start:start + piece_ms
        ]

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as tmp:

            piece_path = tmp.name

            piece.export(
                piece_path,
                format="wav"
            )

        try:

            print(
                f"🇮🇳 Sarvam piece "
                f"{i+1}/{total_pieces}"
            )

            text = _send_to_sarvam(
                piece_path
            )

            if text:
                full_text.append(text)

        finally:

            if os.path.exists(
                piece_path
            ):

                os.remove(piece_path)

    return " ".join(
        full_text
    ).strip()

# ============================================================
# ROUTER
# ============================================================

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    language = language.lower()

    if language in [
        "hinglish",
        "hindi",
        "hi"
    ]:

        print(
            "🇮🇳 Using Sarvam AI"
        )

        return transcribe_chunk_sarvam(
            chunk_path
        )

    print(
        "🌍 Using Whisper"
    )

    return transcribe_chunk_whisper(
        chunk_path
    )

# ============================================================
# FULL TRANSCRIPTION
# ============================================================

def transcribe_all(
    chunks: List[str],
    language: str = "english"
) -> str:

    if not chunks:
        return ""

    print(
        f"\n📝 Transcribing "
        f"{len(chunks)} chunks..."
    )

    start_time = time.time()

    full_transcript = []

    for i, chunk_path in enumerate(
        chunks
    ):

        print(
            f"\n🎤 Chunk "
            f"{i+1}/{len(chunks)}"
        )

        text = transcribe_chunk(
            chunk_path,
            language=language
        )

        if text:
            full_transcript.append(text)

        # ====================================================
        # CLEANUP CHUNK
        # ====================================================

        try:

            if os.path.exists(
                chunk_path
            ):

                os.remove(chunk_path)

        except:
            pass

    final_text = " ".join(
        full_transcript
    ).strip()

    duration = (
        time.time()
        - start_time
    )

    print(
        f"\n✅ Transcription completed "
        f"in {duration:.1f}s"
    )

    return final_text