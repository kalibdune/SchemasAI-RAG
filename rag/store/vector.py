import asyncio
import faiss
import numpy as np
from langchain.embeddings.base import Embeddings
from rag.document.processor import DocumentProcessor
from rag.utils.singleton import SingletonMeta

class VectorStoreManager(metaclass=SingletonMeta):
    def __init__(self, embedding: Embeddings):
        self.embedding_model = embedding
        self.index = None
        self.documents = []
        self.metadatas = []
        self.ids = []

    async def get_or_create_vectorstore(self, documents: list[str]):
        self.ids = [f"id_{i}" for i in range(len(documents))]
        self.documents = [
            doc.page_content if hasattr(doc, "page_content") else str(doc)
            for doc in documents
        ]
        self.metadatas = [
            (
                doc.metadata
                if hasattr(doc, "metadata") and doc.metadata
                else {"default": "value"}
            )
            for doc in documents
        ]
        
        embeddings = await self._get_embeddings(self.documents)
        
        dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings, dtype=np.float32))
        
        return self
        
    async def search_documents(self, query: str, k=4) -> list[dict[str, any]]:
        query_embedding = await self._get_embeddings([query])
        
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), k)
        
        documents = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = {
                    "context": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "id": self.ids[idx],
                    "distance": float(distances[0][i]),
                }
                documents.append(doc)
                
        return documents
        
    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if hasattr(self.embedding_model, "aembed_documents"):
            return await self.embedding_model.aembed_documents(texts)
        else:
            return self.embedding_model.embed_documents(texts)
