# audio_processor.py
import yt_dlp
from pydub import AudioSegment
import os
import ssl
import traceback
import time  
import tempfile
from pathlib import Path
from typing import List

# ============================================================
# Configuration
# ============================================================

DOWNLOAD_DIR = "downloads"
CHUNK_DIR = "chunks"

# Create directories
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# SSL Fix for Render / Cloud environments
ssl._create_default_https_context = ssl._create_unverified_context


def cleanup_old_files(max_age_hours: int = 2):
    """Clean old temporary files to save disk space on Render"""
    for directory in [DOWNLOAD_DIR, CHUNK_DIR]:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                try:
                    if os.path.isfile(file_path):
                        # Delete files older than max_age_hours
                        if os.path.getmtime(file_path) < (time.time() - max_age_hours * 3600):
                            os.remove(file_path)
                except:
                    pass


# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube with robust settings"""
    print(f"🎥 Downloading audio from: {url}")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": False,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_warnings": True,
        "retries": 5,
        "fragment_retries": 5,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web", "ios"]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "geo_bypass": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)

            if not os.path.exists(downloaded_file):
                raise FileNotFoundError(f"Downloaded file not found: {downloaded_file}")

            print(f"✅ Downloaded: {os.path.basename(downloaded_file)}")
            return downloaded_file

    except Exception as e:
        print("❌ YouTube download failed")
        traceback.print_exc()
        if "Sign in to confirm" in str(e):
            raise Exception("YouTube blocked the request. Please upload the video file manually instead.")
        raise Exception(f"YouTube download failed: {str(e)}")


# ============================================================
# Convert to WAV
# ============================================================

def convert_to_wav(input_file: str) -> str:
    """Convert any audio format to WAV"""
    print(f"🎵 Converting to WAV: {os.path.basename(input_file)}")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file = os.path.splitext(input_file)[0] + ".wav"

    try:
        audio = AudioSegment.from_file(input_file)
        # Optimize for Whisper/Sarvam: mono + 16kHz
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        audio.export(output_file, format="wav")
        print(f"✅ Converted to WAV: {os.path.basename(output_file)}")
        return output_file

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Audio conversion failed: {str(e)}")


# ============================================================
# Chunk Audio
# ============================================================

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> List[str]:
    """Split audio into smaller chunks for transcription"""
    print(f"✂️ Chunking audio: {os.path.basename(wav_path)}")

    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    audio = AudioSegment.from_wav(wav_path)
    chunk_length_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[start : start + chunk_length_ms]
        
        chunk_filename = f"{Path(wav_path).stem}_chunk_{i:03d}.wav"
        chunk_path = os.path.join(CHUNK_DIR, chunk_filename)

        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    print(f"✅ Created {len(chunks)} audio chunk(s)")
    return chunks


# ============================================================
# Main Pipeline
# ============================================================

def process_input(source: str) -> List[str]:
    """Main function: Process YouTube URL or Local File"""
    try:
        print("🚀 Starting audio processing...")

        # Optional: Clean old files before processing
        cleanup_old_files(max_age_hours=3)

        # YouTube URL
        if "youtube.com" in source.lower() or "youtu.be" in source.lower():
            print("🔗 YouTube link detected")
            audio_file = download_youtube_audio(source)
        # Local uploaded file
        else:
            print("📁 Local file detected")
            if not os.path.exists(source):
                raise FileNotFoundError(f"Uploaded file not found: {source}")
            audio_file = source

        # Convert to WAV
        wav_path = convert_to_wav(audio_file)

        # Create chunks
        chunks = chunk_audio(wav_path, chunk_minutes=10)

        print(f"✅ Audio processing completed — {len(chunks)} chunk(s) ready")
        return chunks

    except Exception as e:
        print("❌ Audio processing failed")
        traceback.print_exc()
        raise Exception(f"Processing failed: {str(e)}")