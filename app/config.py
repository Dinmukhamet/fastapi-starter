from pathlib import Path

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    database_echo: bool = False
    database_url: PostgresDsn
    debug: bool = False
    secret_key: SecretStr

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="allow"
    )
