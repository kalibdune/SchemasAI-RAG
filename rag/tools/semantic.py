from typing import Dict, Any, Type
from langchain.tools import BaseTool
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, Field
from scipy.spatial.distance import cosine


class SemanticAnalysisInput(BaseModel):
    query: str = Field(..., description="Пользовательский запрос для анализа")

class SemanticTool(BaseTool):
    name: str = "semantic_analyzer"
    description: str = "Анализирует семантику входящего запроса и определяет его тип"
    args_schema: Type[BaseModel] = SemanticAnalysisInput
    embedding_model: Embeddings = Field(exclude=True)
    templates: dict[str, list[str]]
    score_plank: float = 0.5
    
    def __init__(self, embedding_model: Embeddings):
        templates = {
            "create": [
                "создай новую схему", 
                "сгенерируй json схему",
                "нужен новый шаблон",
                "разработай схему для"
            ],
            "edit": [
                "отредактируй схему",
                "измени схему",
                "поправь схему",
                "обнови существующую схему"
            ],
            "irrelevant": [
                "что такое погода",
                "расскажи анекдот",
                "какая сегодня дата"
            ]
        }
        # Pass both parameters to super().__init__
        super().__init__(embedding_model=embedding_model, templates=templates)
        
    def _run(self, query: str) -> Dict[str, Any]:
        """Синхронный запуск инструмента"""
        query_embedding = self.embedding_model.embed_query(query)
        
        best_score = -1
        best_category = "irrelevant"
        
        for category, examples in self.templates.items():
            for example in examples:
                example_embedding = self.embedding_model.embed_query(example)
                similarity = 1 - cosine(query_embedding, example_embedding)
                if similarity > best_score:
                    best_score = similarity
                    best_category = category
        
        if best_score < self.score_plank:
            best_category = "irrelevant"
            
        return {
            "type": best_category,
            "confidence": best_score,
            "is_relevant": best_category != "irrelevant"
        }
        
    async def _arun(self, query: str) -> Dict[str, Any]:
        query_embedding = await self.embedding_model.aembed_query(query)
        
        best_score = -1
        best_category = "irrelevant"
        
        for category, examples in self.templates.items():
            for example in examples:
                example_embedding = await self.embedding_model.aembed_query(example)
                similarity = 1 - cosine(query_embedding, example_embedding)
                if similarity > best_score:
                    best_score = similarity
                    best_category = category
        
        if best_score < self.score_plank:
            best_category = "irrelevant"
            
        return {
            "type": best_category,
            "confidence": best_score,
            "is_relevant": best_category != "irrelevant"
        }