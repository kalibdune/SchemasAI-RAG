import asyncio

import numpy as np
from langchain.embeddings.base import Embeddings


class AsyncChromaEmbeddingAdapter:

    def __init__(self, embedding_model: Embeddings):
        self.embedding_model = embedding_model

    def __call__(self, input: list[str]) -> np.ndarray:
        if not input:
            return np.array([])

        if len(input) == 1:
            return np.array([self.embedding_model.embed_query(input[0])])
        else:
            return np.array(self.embedding_model.embed_documents(input))

    async def acall(self, input: list[str]) -> np.ndarray:
        if not input:
            return np.array([])

        if hasattr(self.embedding_model, "aembed_query") and hasattr(
            self.embedding_model, "aembed_documents"
        ):
            if len(input) == 1:
                return np.array([await self.embedding_model.aembed_query(input[0])])
            else:
                return np.array(await self.embedding_model.aembed_documents(input))
        else:
            return await asyncio.to_thread(self.__call__, input)
