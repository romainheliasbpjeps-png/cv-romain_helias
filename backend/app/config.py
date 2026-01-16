"""
Application Configuration
Manages all configuration using environment variables and Pydantic Settings
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type checking"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="PDF to JSON Converter", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment (development/production)")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )

    # File Upload
    max_upload_size: int = Field(default=50 * 1024 * 1024, description="Max upload size in bytes (50MB)")
    allowed_extensions: List[str] = Field(default=[".pdf"], description="Allowed file extensions")
    upload_dir: Path = Field(default=Path("uploads"), description="Upload directory")
    temp_dir: Path = Field(default=Path("temp"), description="Temporary directory")

    # PDF Processing
    default_dpi: int = Field(default=300, description="Default DPI for PDF rendering")
    max_pages: Optional[int] = Field(default=None, description="Max pages to process (None = unlimited)")

    # OCR
    tesseract_cmd: Optional[str] = Field(default=None, description="Path to tesseract executable")
    ocr_languages: List[str] = Field(
        default=["fra", "eng"],
        description="Available OCR languages"
    )
    default_ocr_lang: str = Field(default="fra", description="Default OCR language")
    ocr_timeout: int = Field(default=300, description="OCR timeout in seconds")

    # Extraction Profiles
    extraction_profiles: dict = Field(
        default={
            "fast": {
                "use_ocr": False,
                "dpi": 150,
                "detect_tables": False,
                "merge_lines": True
            },
            "balanced": {
                "use_ocr": "auto",
                "dpi": 300,
                "detect_tables": True,
                "merge_lines": True
            },
            "accurate": {
                "use_ocr": True,
                "dpi": 600,
                "detect_tables": True,
                "merge_lines": False
            }
        },
        description="Extraction profiles configuration"
    )

    # Performance
    worker_count: int = Field(default=4, description="Number of worker processes")
    worker_timeout: int = Field(default=300, description="Worker timeout in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    @field_validator("upload_dir", "temp_dir")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist"""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
