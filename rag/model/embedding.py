import asyncio

import httpx
from langchain.embeddings.base import Embeddings

from rag.config import config


class Embedding(Embeddings):
    model: str = config.embedding.model
    api_key: str = config.api.key.get_secret_value()
    api_url: str = str(config.api.url)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"model": self.model, "input": text}

        try:
            response = httpx.post(
                self.api_url + "v1/embeddings",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            result = response.json()
            return result["data"][0]["embedding"]

        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {e}")

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = [self.aembed_query(text) for text in texts]
        return await asyncio.gather(*embeddings)

    async def aembed_query(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"model": self.model, "input": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url + "v1/embeddings",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            result = response.json()
            return result["data"][0]["embedding"]