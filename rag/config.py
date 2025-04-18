import os
import time

from pydantic import FilePath
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

os.environ["TZ"] = "UTC"
time.tzset()


class BaseConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class APPConfig(prefix="APP_"):
    document_path: FilePath


class ChromaDB(prefix="DB_"):
    host: str
    port: int


class Config(BaseConfig):
    app: APPConfig
    chroma: ChromaDB


config = Config(chroma=ChromaDB(), app=APPConfig())
