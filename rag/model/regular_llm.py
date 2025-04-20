from rag.config import config
from rag.model.base import BaseLLM


class RegularLLM(BaseLLM):
    model: str = config.llm.model
    temperature: float = config.llm.temperature
    api_key: str = config.api.key.get_secret_value()
    api_url: str = str(config.api.url)

    def __init__(self):
        super().__init__()
