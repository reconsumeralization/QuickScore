from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    A class to manage all the settings for the application.
    Uses pydantic BaseSettings for validation and serialization.
    """
    DB_HOST: Optional[str]
    DB_PORT: Optional[str]
    DB_USERNAME: Optional[str]
    DB_PASSWORD: Optional[str]
    DB_DATABASE: Optional[str]

    SECRET_KEY: Optional[str]
    COHERE_API_KEY: Optional[str]
    WEAVIATE_API_KEY: Optional[str]
    WEAVIATE_URL: Optional[str]

    class Config:
        """
        Internal class for configuring the behaviour of Settings.
        """
        env_file = "./backend/.env"

config = Settings()
