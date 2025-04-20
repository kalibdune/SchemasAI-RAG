
from dataclasses import dataclass
import re
from langchain.llms.base import BaseLLM
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from rag.store.vector import VectorStoreManager
from rag.tools.retriever import RetrieverTool
import json

@dataclass
class CreatorAnswer:
    status: str
    message: str
    schema: str = None
    explanation: str | None = None
    raw_response: str | None = None  # Full response when error occurs


class SchemaCreatorAgent:
    def __init__(
        self,
        llm: BaseLLM,
        vector_store: VectorStoreManager
    ):
        system_prompt = """
            Ты - эксперт по созданию JSON-схем для интеграционной платформы.
            
            Твоя задача - создавать корректные JSON-схемы для различных компонентов интеграционной
            платформы на основе запроса пользователя и доступной документации.
            
            Следуй этим правилам:
            1. Внимательно анализируй запрос пользователя и определяй, какого типа должна быть схема.
            2. Используй документацию для поиска релевантных примеров и структуры схемы.
            3. Создавай корректную схему, следуя структуре из документации.
            4. Проверяй созданную схему на валидность.
            6. Если каких-то данных не хватает для создания схемы, напиши об этом пользователю с просьбой дополнить ответ этими данными. Не упоминай при ответе конкретные названия полей из документации. Проси дополнить формата: \'объяснение поля на русском\' -> \'пример поля\'
        """
        
        self.llm = llm
        self.vector_store = vector_store

        self.retriever_tool = RetrieverTool(vectorstore=self.vector_store)

        creation_template = """
            Задача: создать JSON-схему для интеграционной платформы на основе запроса пользователя.
            
            Запрос пользователя: {query}
            
            Релевантная информация из документации:
            {context}
            
            Создай полную и корректную JSON-схему, соответствующую запросу пользователя.
            Используй предоставленную информацию из документации для правильной структуры схемы.
            При построении схемы учитывай, что она должна в себе содержать: Описание wf/definition, стартеры по запросу пользователя и Activities по запросу пользователя
            Если каких-то данных не хватает для создания схемы, напиши об этом пользователю с просьбой дополнить ответ этими данными в соответствующем поле
            Напиши КОРОТКИЕ пояснения пользователю в соответствующем поле, структуру поля оставь.
            
            Структурируй свой ответ следующим образом:

            ```json
            здесь должна быть полная JSON-схема
            ```
            [# вместо этих слов должен быть вопрос к пользователю ЕСЛИ ТАКОВЫЕ ИМЕЮТСЯ #]

            [/ вместо этих слов должено быть описание схемы ЕСЛИ СХЕМА ИМЕЕТСЯ /]
        """
        
        self.creation_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=creation_template
        )
        self.creation_chain = LLMChain(
            llm=self.llm.with_config(system_prompt=system_prompt),
            prompt=self.creation_prompt,
        )
        
        fix_template = """
            Я создал JSON-схему, но в ней есть ошибки синтаксиса:
            
            {schema_json}
            
            Ошибки:
            {errors}
            
            Пожалуйста, исправь эти ошибки и верни правильную JSON-схему.
            Верни ТОЛЬКО валидный JSON без дополнительных комментариев.
        """
        
        self.fix_prompt = PromptTemplate(
            input_variables=["schema_json", "errors"],
            template=fix_template
        )
        self.fix_chain = LLMChain(
            llm=self.llm,
            prompt=self.fix_prompt
        )
        
    async def process(self, message: dict[str, any]) -> dict[str, any]:
        user_query = message.get("query", "")
        
        if not user_query:
            return {
                "status": "error",
                "message": "Запрос пустой",
                "schema": None
            }
        
        try:
            retriever_result = (await self.retriever_tool.arun(user_query, k=3)).get("context", "")
            definition_schema = (await self.retriever_tool.arun("Описание wf/definition", k=2)).get("context", "")
            context = definition_schema + retriever_result
            
            schema_response = await self.creation_chain.arun(
                query=user_query, 
                context=context
            )
            
            schema_json = self._extract_json(schema_response)
            explanation = self._extract_explanation(schema_response)
            corrections = self._extract_corrections(schema_response)
            
            if not schema_json:
                return {
                    "status": "error",
                    "message": "Не удалось извлечь JSON-схему из ответа",
                    "raw_response": schema_response
                }

            if corrections:
                return {
                    "status": "questions",
                    "message": corrections,
                    "raw_response": schema_response
                }
            
            is_valid = self._check_validity(schema_json)
            
            if not is_valid:
                try:
                    errors = "JSON syntax is invalid"
                    fixed_json = await self.fix_chain.arun(
                        schema_json=schema_json,
                        errors=errors
                    )
                    if self._check_validity(fixed_json):
                        schema_json = fixed_json
                        is_valid = True
                except Exception as fix_error:
                    return {
                        "status": "error",
                        "message": f"Не удалось исправить JSON-схему: {str(fix_error)}",
                        "raw_response": schema_response
                    }
            
            schema_json = schema_json if is_valid else None
            
            return {
                "status": "success" if is_valid else "error",
                "message": "Схема успешно создана" if is_valid else "Ошибка синтаксиса JSON",
                "schema": schema_json,
                "explanation": explanation,
                "raw_response": schema_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка при создании схемы: {str(e)}",
            }
    
    
    def _extract_json(self, response: str) -> str | None:
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        
        if json_match:
            return json_match.group(1).strip()
        
        json_match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        
        if json_match:
            return json_match.group(1).strip()
        
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
        json_match = re.search(json_pattern, response)
        
        if json_match:
            return json_match.group(0)
        
        return None
    
    def _extract_explanation(self, response: str) -> str | None:
        explanations_match = re.search(r"\[\/.*\/\]", response, re.DOTALL)

        if explanations_match:
            return explanations_match.group(0).strip()
        
        return None
    
    def _extract_corrections(self, response: str) -> str | None:
        corrections_match = re.search(r"\[#.*#\]", response, re.DOTALL)

        if corrections_match:
            return corrections_match.group(0).strip()
        
        return None

    def _check_validity(self, json_schema: str) -> bool:
        try:
            json.loads(json_schema)
            return True
        except json.JSONDecodeError:
            return False