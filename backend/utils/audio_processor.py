# audio_processor.py

import os
import ssl
import time
import tempfile
import traceback

from pathlib import Path
from typing import List

import yt_dlp

from pydub import AudioSegment

# ============================================================
# CONFIGURATION
# ============================================================

DOWNLOAD_DIR = "downloads"

CHUNK_DIR = "chunks"

TEMP_DIR = "temp"

# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    CHUNK_DIR,
    exist_ok=True
)

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)

# ============================================================
# SSL FIX FOR CLOUD ENVIRONMENTS
# ============================================================

ssl._create_default_https_context = (
    ssl._create_unverified_context
)

# ============================================================
# CLEANUP OLD FILES
# ============================================================

def cleanup_old_files(
    max_age_hours: int = 2
):

    """Delete old temporary files"""

    now = time.time()

    for directory in [
        DOWNLOAD_DIR,
        CHUNK_DIR,
        TEMP_DIR
    ]:

        if not os.path.exists(directory):
            continue

        for file in os.listdir(directory):

            path = os.path.join(
                directory,
                file
            )

            try:

                if (
                    os.path.isfile(path)
                    and
                    os.path.getmtime(path)
                    < now - max_age_hours * 3600
                ):

                    os.remove(path)

            except:
                pass

# ============================================================
# YOUTUBE DOWNLOAD
# ============================================================

def download_youtube_audio(
    url: str
) -> str:

    print(
        f"🎥 Downloading YouTube audio:\n{url}"
    )

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": os.path.join(
            DOWNLOAD_DIR,
            "%(id)s.%(ext)s"
        ),

        "quiet": True,

        "no_warnings": True,

        "noplaylist": True,

        "nocheckcertificate": True,

        "ignoreerrors": False,

        "retries": 3,

        "fragment_retries": 3,

        "geo_bypass": True,

        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android"
                ]
            }
        },

        "http_headers": {

            "User-Agent":
            "Mozilla/5.0"
        },
    }

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            downloaded_file = (
                ydl.prepare_filename(info)
            )

            if not os.path.exists(
                downloaded_file
            ):

                raise FileNotFoundError(
                    "Download failed"
                )

            print(
                f"✅ Downloaded:\n"
                f"{os.path.basename(downloaded_file)}"
            )

            return downloaded_file

    except Exception as e:

        traceback.print_exc()

        if "Sign in to confirm" in str(e):

            raise Exception(
                "YouTube blocked this request.\n"
                "Please upload the audio/video file manually."
            )

        raise Exception(
            f"YouTube download failed: {str(e)}"
        )

# ============================================================
# CONVERT TO WAV
# ============================================================

def convert_to_wav(
    input_file: str
) -> str:

    print(
        f"🎵 Converting to WAV:\n"
        f"{os.path.basename(input_file)}"
    )

    if not os.path.exists(
        input_file
    ):

        raise FileNotFoundError(
            f"Input file not found:\n{input_file}"
        )

    output_file = os.path.join(
        TEMP_DIR,
        f"{Path(input_file).stem}.wav"
    )

    try:

        audio = AudioSegment.from_file(
            input_file
        )

        # Whisper optimization
        audio = (
            audio
            .set_frame_rate(16000)
            .set_channels(1)
        )

        audio.export(
            output_file,
            format="wav"
        )

        print(
            f"✅ WAV conversion completed"
        )

        return output_file

    except Exception as e:

        traceback.print_exc()

        raise Exception(
            f"Audio conversion failed: {str(e)}"
        )

# ============================================================
# CHUNK AUDIO
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 2
) -> List[str]:

    print(
        f"✂️ Chunking audio..."
    )

    if not os.path.exists(
        wav_path
    ):

        raise FileNotFoundError(
            f"WAV file not found:\n{wav_path}"
        )

    audio = AudioSegment.from_wav(
        wav_path
    )

    chunk_length_ms = (
        chunk_minutes
        * 60
        * 1000
    )

    chunks = []

    for i, start in enumerate(
        range(
            0,
            len(audio),
            chunk_length_ms
        )
    ):

        chunk = audio[
            start:start + chunk_length_ms
        ]

        chunk_filename = (
            f"{Path(wav_path).stem}"
            f"_chunk_{i:03d}.wav"
        )

        chunk_path = os.path.join(
            CHUNK_DIR,
            chunk_filename
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    print(
        f"✅ Created {len(chunks)} chunk(s)"
    )

    # REMOVE LARGE WAV FILE
    try:

        if os.path.exists(wav_path):
            os.remove(wav_path)

    except:
        pass

    return chunks

# ============================================================
# MAIN PIPELINE
# ============================================================

def process_input(
    source
) -> List[str]:

    try:

        print(
            "\n🚀 Starting audio processing..."
        )

        cleanup_old_files(
            max_age_hours=3
        )

        # ====================================================
        # STREAMLIT FILE
        # ====================================================

        if not isinstance(
            source,
            str
        ):

            print(
                "📂 Uploaded file detected"
            )

            suffix = os.path.splitext(
                source.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                dir=TEMP_DIR
            ) as tmp_file:

                tmp_file.write(
                    source.read()
                )

                audio_file = tmp_file.name

            print(
                f"✅ Temp file created:\n"
                f"{audio_file}"
            )

        # ====================================================
        # YOUTUBE URL
        # ====================================================

        elif (
            "youtube.com" in source.lower()
            or
            "youtu.be" in source.lower()
        ):

            print(
                "🔗 YouTube URL detected"
            )

            audio_file = (
                download_youtube_audio(
                    source
                )
            )

        # ====================================================
        # LOCAL FILE
        # ====================================================

        else:

            print(
                "📁 Local file detected"
            )

            if not os.path.exists(
                source
            ):

                raise FileNotFoundError(
                    f"File not found:\n{source}"
                )

            audio_file = source

        # ====================================================
        # CONVERT TO WAV
        # ====================================================

        wav_path = convert_to_wav(
            audio_file
        )

        # ====================================================
        # CREATE CHUNKS
        # ====================================================

        chunks = chunk_audio(
            wav_path,
            chunk_minutes=2
        )

        print(
            "\n✅ Audio processing completed"
        )

        return chunks

    except Exception as e:

        print(
            "\n❌ Audio processing failed"
        )

        traceback.print_exc()

        raise Exception(
            f"Processing failed: {str(e)}"
        )