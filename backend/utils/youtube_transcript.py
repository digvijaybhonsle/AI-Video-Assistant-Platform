import re

from youtube_transcript_api import (
    YouTubeTranscriptApi
)

from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# ============================================================
# EXTRACT VIDEO ID
# ============================================================

def extract_video_id(
    url: str
):

    """
    Extract YouTube video ID
    from different URL formats
    """

    patterns = [

        r"(?:v=|\/)([0-9A-Za-z_-]{11})",

        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",

        r"(?:embed\/)([0-9A-Za-z_-]{11})",

        r"(?:shorts\/)([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url
        )

        if match:
            return match.group(1)

    return None

# ============================================================
# FETCH TRANSCRIPT
# ============================================================

def fetch_youtube_transcript(
    url: str
) -> str:

    """
    Fetch YouTube subtitles
    using YouTube Transcript API
    """

    try:

        video_id = extract_video_id(
            url
        )

        if not video_id:

            raise Exception(
                "Invalid YouTube URL"
            )

        print(
            f"📺 Fetching transcript "
            f"for video:\n{video_id}"
        )

        # ====================================================
        # TRY ENGLISH FIRST
        # ====================================================

        transcript = (
            YouTubeTranscriptApi
            .get_transcript(

                video_id,

                languages=[
                    "en",
                    "en-US",
                    "en-GB"
                ]
            )
        )

        # ====================================================
        # MERGE TEXT
        # ====================================================

        text = " ".join(

            chunk["text"]

            for chunk in transcript

            if chunk["text"].strip()
        )

        if not text.strip():

            raise Exception(
                "Transcript is empty"
            )

        print(
            "✅ Transcript fetched successfully"
        )

        return text

    # ========================================================
    # SPECIFIC ERRORS
    # ========================================================

    except NoTranscriptFound:

        raise Exception(
            "No transcript/subtitles available "
            "for this video."
        )

    except TranscriptsDisabled:

        raise Exception(
            "Subtitles are disabled "
            "for this video."
        )

    except VideoUnavailable:

        raise Exception(
            "This YouTube video is unavailable."
        )

    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        raise Exception(
            f"Transcript fetch failed: {str(e)}"
        )