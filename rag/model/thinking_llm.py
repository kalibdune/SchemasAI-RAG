from rag.config import config
from rag.model.base import BaseLLM


class ThinkingLLM(BaseLLM):
    model: str = config.thinking_llm.model
    temperature: float = config.thinking_llm.temperature
    api_key: str = config.api.key.get_secret_value()
    api_url: str = str(config.api.url)

    def __init__(self):
        super().__init__()


llm = ThinkingLLM()
print(
    llm.invoke(
        "расскажи сказку", system_prompt="ты рассказчик дестких сказок на русском"
    )
)
