# Location: backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgenticOps Backend"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    GEMINI_API_KEY: str 
    
    # Instruct Pydantic to ignore external tracing keys (.env variables)
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Allow Langfuse/LangSmith variables to pass to the environment safely
    )

settings = Settings()