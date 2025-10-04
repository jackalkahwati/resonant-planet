"""
Application settings and configuration management.
"""
import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Modulus integration
    use_local_modulus: bool = True
    modulus_local_path: str = "physics/local_modulus"

    # Demo and data
    demo_mode: bool = True
    demo_datasets_path: str = "assets/demos"
    upload_dir: str = "uploads"
    artifacts_dir: str = "run_artifacts"

    # Job execution
    job_backend: Literal["background", "celery"] = "background"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Database
    database_url: str = "sqlite:///./resonant_worlds.db"

    # Models
    qwen_weights_path: str = "assets/weights/qwen_small.pt"
    classifier_model_path: str = "assets/models/xgb_classifier.json"
    rl_policy_path: str = "assets/models/rl_policy.json"

    # Logging
    log_level: str = "INFO"

    @property
    def base_dir(self) -> Path:
        """Get the backend base directory."""
        return Path(__file__).parent.parent

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        dirs = [
            self.base_dir / self.upload_dir,
            self.base_dir / self.artifacts_dir,
            self.base_dir / self.demo_datasets_path,
            self.base_dir / Path(self.qwen_weights_path).parent,
            self.base_dir / Path(self.classifier_model_path).parent,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
