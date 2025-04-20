import asyncio
from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from rag.store.vector import VectorStoreManager

class RetrieverInput(BaseModel):
    query: str = Field(..., description="Запрос для поиска контекста")
    k: int = Field(default=5, description="Количество результатов для возврата")

class RetrieverTool(BaseTool):
    name: str = "documentation_retriever"
    description: str = "Ищет релевантную информацию в документации по интеграционной платформе"
    args_schema: Type[BaseModel] = RetrieverInput
    vectorstore: VectorStoreManager
    
    def __init__(self, vectorstore: VectorStoreManager):
        super().__init__(vectorstore=vectorstore)
        self.vectorstore = vectorstore
            
    def _run(self, query: str, k: int = 5) -> dict[str, any]:
        asyncio.get_running_loop().run_until_complete(self._arun(query, k))
        
    async def _arun(self, query: str, k: int = 5) -> dict[str, any]:
        try:
            return await self.vectorstore.search_documents(query, k)            
        except Exception as e:
            return {
                "context": "",
                "metadata": [],
                "chunks_count": 0,
                "error": str(e)
            }