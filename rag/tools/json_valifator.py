import asyncio
from typing import Dict, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json

class ValidatorInput(BaseModel):
    json_str: str = Field(..., description="JSON строка для валидации")
    schema_type: Optional[str] = Field(None, description="Тип схемы для проверки")

class JsonValidatorTool(BaseTool):
    name: str = "json_validator"
    description: str = "Проверяет корректность JSON-схемы"
    args_schema: Type[BaseModel] = ValidatorInput
    
    def _run(self, json_str: str) -> Dict[str, Any]:
        result = {"valid": False, "errors": []}
        try:
            json.loads(json_str)
            result["valid_syntax"] = True
        except json.JSONDecodeError as e:
            result["valid_syntax"] = False
            result["errors"].append(f"Ошибка синтаксиса JSON: {str(e)}")
            return result
                        
        return result
        
    async def _arun(self, json_str: str) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self._run(json_str))
        