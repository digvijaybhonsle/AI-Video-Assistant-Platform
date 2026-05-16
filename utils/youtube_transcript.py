# utils/youtube_transcript.py

from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def fetch_youtube_transcript(url):
    video_id = extract_video_id(url)

    if not video_id:
        raise Exception("Invalid YouTube URL")

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    text = " ".join([x["text"] for x in transcript])

    return text