"""Application settings and configuration"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Phase III AI Chatbot"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str

    # LLM Configuration (LiteLLM)
    # Format: "provider/model-name" (e.g., "openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet-20240620")
    llm_model: str = "openai/gpt-4o-mini"
    llm_api_key: Optional[str] = None  # API key for the LLM provider

    # Legacy OpenAI Configuration (for backward compatibility)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_model_config(self) -> tuple[str, str]:
        """
        Get model and API key configuration.

        Returns:
            Tuple of (model, api_key)
        """
        # Use LiteLLM config if available
        if self.llm_api_key:
            return self.llm_model, self.llm_api_key

        # Fallback to OpenAI config
        if self.openai_api_key:
            return f"openai/{self.openai_model}", self.openai_api_key

        raise ValueError("No LLM API key configured. Set LLM_API_KEY or OPENAI_API_KEY in .env")


settings = Settings()
