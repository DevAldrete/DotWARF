from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "Dotwarf API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security
    ADMIN_API_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://dotwarf:dotwarf@localhost:5432/dotwarf"

    # LiteLLM / AI
    LITELLM_MODEL: str = "openai/gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    AI_SYSTEM_PROMPT: str = (
        "You are a helpful assistant for Dotwarf, a digital agency specializing in "
        "AI solutions including chatbots, agents, workflow automations, model fine-tuning, "
        "website creation, API development, and custom freelance projects. "
        "Be concise, professional, and guide visitors toward booking a consultation."
    )

    # Rate limiting (requests per window)
    CHAT_RATE_LIMIT: str = "20/hour"
    CONTACT_RATE_LIMIT: str = "5/hour"

    # SMTP / Gmail
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""  # Gmail App Password
    SMTP_FROM_EMAIL: str = ""
    CONTACT_RECIPIENT_EMAIL: str = ""  # Your inbox

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
