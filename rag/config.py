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


class JsonConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
        env_file_encoding="utf-8",
        json_schema_extra={"format_settings": {"hide_docs": True}},
    )

    @classmethod
    def from_json(cls, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


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


class PropmtpsTable(JsonConfig):
    coordinator: str


class Document(BaseConfig, env_prefix="DOC_"):
    path: AnyUrl | FilePath


class ChromaDB(BaseConfig, env_prefix="DB_"):
    host: str
    port: int


class Config(BaseConfig):
    document: Document
    chroma: ChromaDB
    llm: LLM
    thinking_llm: ThinkingLLM
    embedding: Embedding
    api: API
    propmpts_table: PropmtpsTable


config = Config(
    chroma=ChromaDB(),
    document=Document(),
    llm=LLM(),
    thinking_llm=ThinkingLLM(),
    embedding=Embedding(),
    api=API(),
    propmpts_table=PropmtpsTable.from_json(BASE_PATH / "static" / "prompts.json"),
)
