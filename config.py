from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str
    DATABASE: str
    USER: str
    PASSWORD: str
     
    class Config:
        env_file = ".env"

settings = Settings()
