from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.embeddings.base import Embeddings
from rag.tools.semantic import SemanticTool
from rag.agents.schema_creator import SchemaCreatorAgent
from dataclasses import dataclass

@dataclass
class CoordinatorAnswer:
    status: str
    message: str
    action: str | None = None
    query: str | None = None

class CoordinatorAgent():
    def __init__(self, llm: BaseLLM, embedding_model: Embeddings):
        system_prompt = """
            Ты - интеллектуальный координатор в системе, которая работает с JSON-схемами для 
            интеграционной платформы. Твоя задача - анализировать запросы пользователя и 
            определять их тип:
            1. Создание новой JSON-схемы (create)
            2. Редактирование существующей JSON-схемы (edit)
            3. Нерелевантные запросы (irrelevant)
            
            Если запрос относится к созданию или редактированию схем, ты должен перенаправить 
            его соответствующему агенту.
            
            Для запросов, не относящихся к работе с JSON-схемами, объясни, что можешь помочь 
            только с созданием и редактированием JSON-схем для интеграционной платформы.
        """
        
        tools = [SemanticTool(embedding_model=embedding_model)]
        
        self.name = "coordinator"
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools
        self.embedding_model = embedding_model
        
        self.semantic_tool = self.tools[0]
        
        irrelevant_template = """
            Пользователь задал следующий вопрос: "{query}"
            
            Этот запрос не связан с созданием или редактированием JSON-схем для интеграционной
            платформы. Объясни вежливо, что ты можешь помочь только с этими задачами.
        """
        self.irrelevant_prompt = PromptTemplate(
            input_variables=["query"],
            template=irrelevant_template
        )
        self.irrelevant_chain = self.irrelevant_prompt | self.llm
        
    async def process(self, message: dict[str, any]) -> CoordinatorAnswer:
        user_query = message.get("query", "")
        
        if not user_query:
            return CoordinatorAnswer(**{
                "status": "error",
                "message": "Запрос пустой",
                "action": None,
                "query": None
            })
            
        semantic_result = await self.semantic_tool._arun(user_query)
        
        query_type = semantic_result.get("type", "irrelevant")
        
        if query_type == "create":
            return CoordinatorAnswer(**{
                "status": "success",
                "message": "Запрос на создание JSON-схемы",
                "action": "create",
                "query": user_query,
            })
        elif query_type == "edit":
            return CoordinatorAnswer(**{
                "status": "success",
                "message": "Запрос на редактирование JSON-схемы",
                "action": "edit",
                "query": user_query,
            })
        else:
            irrelevant_response = await self.irrelevant_chain.ainvoke({"query": user_query})
            
            return CoordinatorAnswer(**{
                "status": "irrelevant",
                "message": irrelevant_response,
                "action": "none",
                "query": user_query,
            })