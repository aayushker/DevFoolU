"""Core configuration for the FastAPI backend"""

from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
    
    # API Settings
    APP_NAME: str = "DevFoolU API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = "*"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # MongoDB Settings
    MONGODB_URL: str = ""  # Set via environment variable
    MONGODB_DATABASE: str = "DevFoolU"
    MONGODB_COLLECTION: str = "Cluster0"
    MONGODB_TIMEOUT: int = 30000
    MONGODB_INGEST_JOBS_COLLECTION: str = "scrape_jobs"
    MONGODB_INGEST_URLS_COLLECTION: str = "scrape_job_urls"
    
    # Embedding Model Settings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Auth0 Settings
    AUTH0_DOMAIN: str = ""
    AUTH0_API_AUDIENCE: str = ""
    AUTH0_ISSUER: str = ""
    AUTH0_ALGORITHMS: str = "RS256"
    
    # Scraper Settings (from scraper module)
    SCRAPER_BASE_URL: str = "https://devfolio.co"
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT_MS: int = 45000
    SCRAPER_PAGE_READY_TIMEOUT_MS: int = 12000
    SCRAPER_NAVIGATION_WAIT_UNTIL: str = "domcontentloaded"
    SCRAPER_BLOCK_RESOURCE_TYPES: str = "image,media,font"
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_RETRY_BACKOFF: float = 3.0
    SCRAPER_CONCURRENCY: int = 6
    SCRAPER_RATE_DELAY_MIN: float = 0.5
    SCRAPER_RATE_DELAY_MAX: float = 1.8
    
    # Similarity Search Settings
    SIMILARITY_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity score
    
    # Gemini AI Settings
    GEMINI_API_KEY: str = ""  # Set via environment variable
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Free tier model
    GEMINI_MAX_OUTPUT_TOKENS: int = 200  # ~150 words
    GEMINI_TEMPERATURE: float = 0.7
    
    # Bulk Processing Settings
    BULK_BATCH_SIZE: int = 50
    BULK_MAX_PROJECTS: int = 1000

    # Mass Ingestor Settings
    MASS_INGEST_ENABLED: bool = True
    MASS_INGEST_ON_STARTUP: bool = True
    MASS_INGEST_STARTUP_MODE: str = "incremental"  # backfill | incremental
    MASS_INGEST_TARGET_PROJECTS: int = 97000
    MASS_INGEST_INCREMENTAL_TARGET_PROJECTS: int = 93000
    MASS_INGEST_BATCH_SIZE: int = 100
    MASS_INGEST_DISCOVERY_HEARTBEAT_SECONDS: int = 5
    MASS_INGEST_GENERATE_EMBEDDINGS: bool = True
    MASS_INGEST_SKIP_EXISTING_PROJECT_URLS: bool = True
    MASS_INGEST_MAX_URL_ATTEMPTS: int = 5
    MASS_INGEST_RETRY_BACKOFF_BASE_SECONDS: float = 15.0
    MASS_INGEST_RETRY_BACKOFF_MAX_SECONDS: float = 900.0
    MASS_INGEST_DEFAULT_CONCURRENCY: int = 8
    MASS_INGEST_QOS_MIN_CONCURRENCY: int = 2
    MASS_INGEST_QOS_MAX_CONCURRENCY: int = 20
    MASS_INGEST_QOS_FAILURE_THRESHOLD: float = 0.25
    MASS_INGEST_QOS_RECOVERY_THRESHOLD: float = 0.05
    MASS_INGEST_QOS_DELAY_MIN: float = 0.6
    MASS_INGEST_QOS_DELAY_MAX: float = 2.2
    MASS_INGEST_QOS_DELAY_CAP: float = 6.0
    MASS_INGEST_ADMIN_TOKEN: str = ""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    SCRAPER_DIR: Path = BASE_DIR / "scraper"
    LOGS_DIR: Path = BASE_DIR / "backend" / "logs"
    TEMP_DIR: Path = BASE_DIR / "backend" / "temp"
    
    def model_post_init(self, __context):
        """Create necessary directories after model initialization"""
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
