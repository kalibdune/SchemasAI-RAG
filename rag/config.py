import os
import time
from pathlib import Path

from pydantic import AnyUrl, FilePath, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

os.environ["TZ"] = "UTC"
time.tzset()
BASE_PATH = Path().absolute() / "rag"


class BaseConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class LLM(BaseConfig, env_prefix="LLM_"):
    model: str
    temperature: float


class ThinkingLLM(BaseConfig, env_prefix="THINKING_LLM_"):
    model: str
    temperature: float


class Embedding(BaseConfig, env_prefix="EMBEDDING_"):
    model: str


class API(BaseConfig, env_prefix="API_"):
    url: AnyUrl
    key: SecretStr


class Document(BaseConfig, env_prefix="DOC_"):
    path: AnyUrl | FilePath


class RabbitConfig(BaseConfig, env_prefix="RABBIT_"):
    host: str
    user: str
    password: SecretStr
    port: int

    @property
    def get_url(self) -> str:
        return f"amqp://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/"


class Config(BaseConfig):
    document: Document
    llm: LLM
    thinking_llm: ThinkingLLM
    embedding: Embedding
    api: API
    rabbit: RabbitConfig


config = Config(
    document=Document(),
    llm=LLM(),
    thinking_llm=ThinkingLLM(),
    embedding=Embedding(),
    api=API(),
    rabbit=RabbitConfig(),
)
