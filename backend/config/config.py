from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Pydantic model for environment configuration.
    
    Attributes:
    DB_HOST (str, optional): Database host.
    DB_PORT (int, optional): Database port.
    DB_USERNAME (str, optional): Database username.
    DB_PASSWORD (str, optional): Database password.
    DB_DATABASE (str, optional): Database name.

    SECRET_KEY (str, optional): Secret key for the application.
    COHERE_API_KEY (str, optional): API key for Cohere.
    WEAVIATE_API_KEY (str, optional): API key for Weaviate.
    WEAVIATE_URL (str, optional): URL for Weaviate.
    """

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_DATABASE: Optional[str] = None

    SECRET_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    WEAVIATE_API_KEY: Optional[str] = None
    WEAVIATE_URL: Optional[str] = None

    class Config:
        """
        Configuration for Pydantic model.
        This class is used to specify the location of the environment file.
        """
        env_file = "./backend/.env"
