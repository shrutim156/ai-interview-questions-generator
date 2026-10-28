from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "models/gemini-3.6-flash"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    PORT: int = 8000

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
 
