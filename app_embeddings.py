from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Protocol

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingProviderError(RuntimeError):
    pass


class EmbeddingProvider(Protocol):
    name: str

    def embed_text(self, text: str, corpus: list[str]) -> list[float]:
        raise NotImplementedError


class TfidfEmbeddingProvider:
    name = "tfidf"

    def embed_text(self, text: str, corpus: list[str]) -> list[float]:
        base_corpus = corpus or [text]
        vectorizer = TfidfVectorizer(stop_words="english")
        vectorizer.fit(base_corpus)
        vector = vectorizer.transform([text])
        return vector.toarray()[0].tolist()


@dataclass
class OpenAIEmbeddingProvider:
    api_key: str
    model: str = "text-embedding-3-small"
    base_url: str = "https://api.openai.com/v1"
    name: str = "openai"

    def embed_text(self, text: str, corpus: list[str]) -> list[float]:
        try:
            response = httpx.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": text},
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingProviderError("OpenAI embedding request failed.") from exc
        payload = response.json()
        return payload["data"][0]["embedding"]


def get_embedding_provider() -> EmbeddingProvider:
    provider = os.getenv("EMBEDDING_PROVIDER", "tfidf").lower()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingProviderError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            )
        return OpenAIEmbeddingProvider(api_key=api_key)
    if provider == "tfidf":
        return TfidfEmbeddingProvider()
    raise EmbeddingProviderError(f"Unknown embedding provider: {provider}")
