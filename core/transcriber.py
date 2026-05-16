# transcriber.py
import whisper
import os
import requests
import tempfile
from pathlib import Path
from typing import List
import time

from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

# ========================= CONFIG =========================
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

# Sarvam limit is 30s. We use 25s for safety margin.
SARVAM_PIECE_SECONDS = 25

_model = None


def load_whisper_model():
    """Load Whisper model with caching"""
    global _model
    if _model is None:
        print(f"🚀 Loading Whisper model: {WHISPER_MODEL} ... (This may take 10-30 seconds)")
        start_time = time.time()
        _model = whisper.load_model(WHISPER_MODEL)
        print(f"✅ Whisper model loaded in {time.time() - start_time:.1f} seconds")
    return _model


def transcribe_chunk_whisper(chunk_path: str) -> str:
    """Transcribe using local Whisper model"""
    model = load_whisper_model()
    try:
        result = model.transcribe(
            chunk_path, 
            task="transcribe",
            language=None,           # Auto-detect
            fp16=False               # Better for CPU
        )
        return result["text"].strip()
    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return f"[Whisper Error: {str(e)[:100]}]"


def _send_to_sarvam(piece_path: str) -> str:
    """Send single audio piece to Sarvam API"""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set")

    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (Path(piece_path).name, f, "audio/wav")}
        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }

        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=90
        )

    if not response.ok:
        print(f"❌ Sarvam API Error {response.status_code}: {response.text}")
        response.raise_for_status()

    return response.json().get("transcript", "").strip()


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """Split long audio into ≤25s pieces for Sarvam API"""
    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000
    full_text = []

    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start : start + piece_ms]
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            piece_path = tmp.name
            piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i+1}/{total_pieces} ({len(piece)/1000:.1f}s)")
            text = _send_to_sarvam(piece_path)
            full_text.append(text)
        finally:
            # Cleanup
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return " ".join(full_text).strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """Main routing function"""
    language = language.lower()
    
    if language in ["hinglish", "hi", "hindi"]:
        print("🇮🇳 Using Sarvam AI (Hinglish support)")
        return transcribe_chunk_sarvam(chunk_path)
    else:
        print("🌍 Using Whisper (English)")
        return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: List[str], language: str = "english") -> str:
    """Transcribe all chunks and combine"""
    if not chunks:
        return ""

    print(f"Starting transcription of {len(chunks)} chunks using {language} engine...")
    start_time = time.time()

    full_transcript = []

    for i, chunk_path in enumerate(chunks):
        print(f"📝 Transcribing chunk {i+1}/{len(chunks)}...")
        text = transcribe_chunk(chunk_path, language=language)
        full_transcript.append(text)

    final_text = " ".join(full_transcript).strip()
    
    duration = time.time() - start_time
    print(f"✅ Transcription completed in {duration:.1f} seconds")
    
    return final_text