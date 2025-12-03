"""
Configuration settings for OmniSupply platform.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CHROMA_DIR: Path = DATA_DIR / "chroma"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        env="OPENAI_EMBEDDING_MODEL"
    )

    # Database
    DATABASE_URL: str = Field(
        default="duckdb:///data/omnisupply.db",
        env="DATABASE_URL"
    )
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")

    # Opik (Observability)
    OPIK_PROJECT_NAME: str = Field(default="omnisupply", env="OPIK_PROJECT_NAME")
    OPIK_WORKSPACE: Optional[str] = Field(default=None, env="OPIK_WORKSPACE")

    # Agent Settings
    AGENT_TEMPERATURE: float = Field(default=0.2, env="AGENT_TEMPERATURE")
    AGENT_MAX_TOKENS: int = Field(default=6000, env="AGENT_MAX_TOKENS")
    AGENT_TIMEOUT: int = Field(default=120, env="AGENT_TIMEOUT")  # seconds

    # Supervisor Settings
    SUPERVISOR_PARALLEL_EXECUTION: bool = Field(default=True, env="SUPERVISOR_PARALLEL_EXECUTION")
    SUPERVISOR_MAX_AGENTS: int = Field(default=5, env="SUPERVISOR_MAX_AGENTS")

    # API Settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    API_WORKERS: int = Field(default=1, env="API_WORKERS")

    # Redis (for Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Scheduling
    DAILY_REPORT_HOUR: int = Field(default=8, env="DAILY_REPORT_HOUR")
    DAILY_REPORT_MINUTE: int = Field(default=0, env="DAILY_REPORT_MINUTE")
    RISK_CHECK_INTERVAL_MINUTES: int = Field(default=15, env="RISK_CHECK_INTERVAL_MINUTES")

    # Email Settings (for alerts)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM: str = Field(default="omnisupply@company.com", env="SMTP_FROM")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def ensure_directories(self):
        """Create necessary directories"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
