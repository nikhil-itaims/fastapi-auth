from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os
load_dotenv()

CLIENT_ORIGINS = list(filter(None, os.getenv("CLIENT_ORIGINS").split(",")))

class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_username: str
    db_password: str
    db_name: str
    secret_key: str
    oauth_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    client_origin: list = CLIENT_ORIGINS

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()
