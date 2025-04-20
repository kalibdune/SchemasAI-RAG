import asyncio
from typing import List, Optional

import httpx
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.llms import LLM


class BaseLLM(LLM):
    model: str
    temperature: float
    api_key: str
    api_url: str

    def __init__(self):
        super().__init__()

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        system_prompt = kwargs.pop("system_prompt", "")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "use", "content": prompt},
            ],
            "temperature": self.temperature,
        }
        # Add any additional parameters
        print(payload)
        for key, value in kwargs.items():
            payload[key] = value

        try:
            response = httpx.post(
                self.api_url + "v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {e}")

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        system_prompt = kwargs.pop("system_prompt", "")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "use", "content": prompt},
            ],
            "temperature": self.temperature,
        }
        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url + "v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"Error calling LLM API asynchronously: {e}")

    @property
    def _llm_type(self) -> str:
        return self.model
