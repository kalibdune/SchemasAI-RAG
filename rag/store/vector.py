import chromadb
from langchain.embeddings.base import Embeddings

from rag.config import config
from rag.store.adapters import AsyncChromaEmbeddingAdapter


class VectorStoreManager:
    host: str = config.db.host
    port: int = config.db.port

    def __init__(self, embedding: Embeddings):

        self.embedding_model = AsyncChromaEmbeddingAdapter(embedding)

        self.collection_name = "document_collection2"
        self.client = None

    async def initialize(self) -> "VectorStoreManager":
        self.client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)
        return self

    async def get_or_create_vectorstore(self, documents: list[str]):
        try:
            collection = await self.client.get_collection(
                name=self.collection_name, embedding_function=self.embedding_model
            )
        except Exception as e:
            if "already exists" in str(e):
                collection = await self.client.get_collection(
                    name=self.collection_name, embedding_function=self.embedding_model
                )
            else:
                raise e

        ids = [f"id_{i}" for i in range(len(documents))]
        texts = [
            doc.page_content if hasattr(doc, "page_content") else str(doc)
            for doc in documents
        ]
        metadatas = [
            (
                doc.metadata
                if hasattr(doc, "metadata") and doc.metadata
                else {"default": "value"}
            )
            for doc in documents
        ]

        await collection.add(ids=ids, documents=texts, metadatas=metadatas)

        self.collection = collection

        return collection

    async def search_documents(self, query: str, k=4):

        results = await self.collection.query(query_texts=[query], n_results=k)

        documents = []
        for i in range(len(results["documents"][0])):
            doc = {
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "id": results["ids"][0][i],
                "distance": (
                    results["distances"][0][i] if "distances" in results else None
                ),
            }
            documents.append(doc)

        return documents


import asyncio

from rag.document.processor import DocumentProcessor
from rag.model.embedding import Embedding


async def main():
    embedding = Embedding()
    processor = DocumentProcessor("./rag/static/IntegrationDoc.txt")

    documents = processor.load_document()

    print("start")
    store_manager = await VectorStoreManager(embedding).initialize()
    print("store init")
    store = await store_manager.get_or_create_vectorstore(documents)
    print("store loaded")
    res = await store_manager.search_documents(
        "подключение к раббиту черз очередь message kafka", 2
    )
    print("searched")
    for r in res:
        print("/////\n\n\n", res, "/////\n\n\n")


asyncio.run(main())
