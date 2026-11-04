import os
import re
import unicodedata


class TextEmbeddingService:
    _vectors = {}

    def __init__(self):
        self.model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.backend = "openai"

    @staticmethod
    def tokens(text: str) -> list[str]:
        normalized = unicodedata.normalize("NFKD", text.lower().replace("đ", "d"))
        return re.findall(r"[a-z0-9]+", "".join(char for char in normalized if not unicodedata.combining(char)))

    def embedMany(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Text search needs OPENAI_API_KEY in .env")
        pending = list(dict.fromkeys(text for text in texts if (self.model, text) not in self._vectors))
        if pending:
            try:
                from openai import OpenAI
                response = OpenAI(api_key=api_key, timeout=30, max_retries=0).embeddings.create(
                    model=self.model, input=pending)
            except Exception as error:
                raise ValueError("OpenAI text embedding is unavailable; check the API key and connection") from error
            embeddings = sorted(response.data, key=lambda item: item.index)
            if len(embeddings) != len(pending):
                raise ValueError("OpenAI returned an incomplete embedding response")
            for text, embedding in zip(pending, embeddings):
                self._vectors[self.model, text] = embedding.embedding
        return [self._vectors[self.model, text] for text in texts]

    def embed(self, text: str) -> list[float]:
        return self.embedMany([text])[0]
