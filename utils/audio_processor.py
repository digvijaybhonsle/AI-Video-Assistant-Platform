import yt_dlp
from pydub import AudioSegment
import os
import ssl
import traceback

# ============================================================
# Directories
# ============================================================

DOWNLOAD_DIR = "downloads"
CHUNK_DIR = "chunks"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# ============================================================
# SSL Fix for Hugging Face / Cloud Environments
# ============================================================

ssl._create_default_https_context = ssl._create_unverified_context

# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(url: str) -> str:

    print(f"🎥 Downloading from URL: {url}")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        "quiet": True,
        "noplaylist": True,

        # SSL / Cloud fixes
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_warnings": True,

        # Retry logic
        "retries": 10,
        "fragment_retries": 10,
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            if info is None:
                raise Exception("Failed to extract YouTube video information.")

            downloaded_file = ydl.prepare_filename(info)

            print(f"✅ Downloaded file path: {downloaded_file}")

            if not os.path.exists(downloaded_file):
                raise FileNotFoundError(
                    f"Downloaded audio file not found: {downloaded_file}"
                )

            return downloaded_file

    except Exception as e:

        print("❌ YouTube download failed")
        traceback.print_exc()

        raise Exception(f"YouTube download failed: {str(e)}")


# ============================================================
# Convert Audio To WAV
# ============================================================

def convert_to_wav(input_file: str) -> str:

    print(f"🎵 Converting file: {input_file}")

    if input_file is None:
        raise ValueError("Input file is None.")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file = os.path.splitext(input_file)[0] + ".wav"

    try:

        audio = AudioSegment.from_file(input_file)

        audio.export(output_file, format="wav")

        print(f"✅ WAV saved at: {output_file}")

        return output_file

    except Exception as e:

        print("❌ WAV conversion failed")
        traceback.print_exc()

        raise Exception(f"WAV conversion failed: {str(e)}")


# ============================================================
# Chunk Audio
# ============================================================

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    print(f"✂️ Chunking WAV file: {wav_path}")

    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    audio = AudioSegment.from_wav(wav_path)

    chunk_length_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):

        chunk = audio[start:start + chunk_length_ms]

        chunk_path = os.path.join(
            CHUNK_DIR,
            f"{os.path.splitext(os.path.basename(wav_path))[0]}_chunk_{i}.wav"
        )

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    print(f"✅ Generated {len(chunks)} chunk(s)")

    if len(chunks) == 0:
        raise Exception("No audio chunks were created.")

    return chunks


# ============================================================
# Main Processing Pipeline
# ============================================================

def process_input(source: str) -> list:

    try:

        # ----------------------------------------------------
        # YouTube URL
        # ----------------------------------------------------

        if "youtube.com" in source or "youtu.be" in source:

            print("🎥 Detected YouTube URL")

            downloaded_file = download_youtube_audio(source)

            wav_path = convert_to_wav(downloaded_file)

        # ----------------------------------------------------
        # Local File
        # ----------------------------------------------------

        else:

            print("📁 Detected local file")

            wav_path = convert_to_wav(source)

        # ----------------------------------------------------
        # Chunk Audio
        # ----------------------------------------------------

        chunks = chunk_audio(wav_path)

        print(f"✅ Audio ready — {len(chunks)} chunk(s) created.")

        return chunks

    except Exception as e:

        print("❌ FULL PROCESSING ERROR")
        traceback.print_exc()

        raise Exception(f"Audio processing failed: {str(e)}")