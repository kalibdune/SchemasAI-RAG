import json
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


class DB(BaseConfig, env_prefix="DB_"):
    host: str
    port: int

class Redis(BaseConfig, env_prefix="REDIS_"):
    host: str
    port: int

    @property
    def get_redis_url(self):
        return f"redis://{self.host}:{self.port}"

class Config(BaseConfig):
    document: Document
    db: DB
    llm: LLM
    thinking_llm: ThinkingLLM
    embedding: Embedding
    api: API
    redis: Redis


config = Config(
    db=DB(),
    document=Document(),
    llm=LLM(),
    thinking_llm=ThinkingLLM(),
    embedding=Embedding(),
    api=API(),
    redis=Redis()
)
