import logging
import os
from pathlib import Path


class SpeechToTextService:
    def transcribe(self, audioReference: str) -> str:
        if audioReference.startswith("transcript:"):
            return audioReference.removeprefix("transcript:").strip()
        raise ValueError("Use browser voice recognition or enter a simulated transcript")

    def transcribeAudio(self, content: bytes, filename: str, content_type: str) -> str:
        allowed = {".webm": {"audio/webm"}, ".wav": {"audio/wav", "audio/x-wav"},
                   ".mp3": {"audio/mpeg", "audio/mp3"}, ".mp4": {"audio/mp4"},
                   ".m4a": {"audio/mp4", "audio/x-m4a"}}
        mime = content_type.split(";", 1)[0].lower()
        if mime not in allowed.get(Path(filename).suffix.lower(), set()):
            raise ValueError("Upload a WebM, WAV, MP3, MP4 or M4A audio file")
        if not content or len(content) > 10 * 1024 * 1024:
            raise ValueError("Audio must be between 1 byte and 10 MB")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Audio transcription needs an OpenAI API key; type the transcript instead")
        try:
            from openai import OpenAI
            response = OpenAI(api_key=api_key, timeout=40, max_retries=0).audio.transcriptions.create(
                model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-transcribe"),
                file=(filename, content, mime))
        except Exception as error:
            logging.getLogger(__name__).warning("Audio transcription unavailable: %s", type(error).__name__)
            raise ValueError("Audio transcription is unavailable; type the transcript instead") from error
        transcript = response.text.strip()
        if not transcript:
            raise ValueError("No speech was detected; try again or type the transcript")
        return transcript[:500]

