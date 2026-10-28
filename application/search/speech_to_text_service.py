class SpeechToTextService:
    def transcribe(self, audioReference: str) -> str:
        if audioReference.startswith("transcript:"):
            return audioReference.removeprefix("transcript:").strip()
        raise ValueError("Use browser voice recognition or enter a simulated transcript")

