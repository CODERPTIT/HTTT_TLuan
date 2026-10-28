import hashlib
import re
import unicodedata
from math import sqrt


class TextEmbeddingService:
    @staticmethod
    def tokens(text: str) -> list[str]:
        normalized = unicodedata.normalize("NFKD", text.lower())
        return re.findall(r"[a-z0-9]+", "".join(char for char in normalized if not unicodedata.combining(char)))

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * 256
        for token in self.tokens(text):
            position = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % len(vector)
            vector[position] += 1
        length = sqrt(sum(value * value for value in vector)) or 1
        return [value / length for value in vector]

