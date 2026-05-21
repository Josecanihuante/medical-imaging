from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    MODEL_PATH: str
    SECRET_KEY: str
    ALLOWED_ORIGINS: List[str]
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()