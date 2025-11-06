"""
Application configuration using Pydantic settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, validator
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Diamond OA Journal"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: EmailStr
    SMTP_FROM_NAME: str

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_MANUSCRIPT_FORMATS: str = "pdf,doc,docx,tex,zip"

    @property
    def allowed_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.ALLOWED_MANUSCRIPT_FORMATS.split(",")]

    # DOI
    DOI_PREFIX: str
    DOI_USERNAME: Optional[str] = None
    DOI_PASSWORD: Optional[str] = None
    DOI_API_URL: str = "https://api.crossref.org"
    DOI_TEST_MODE: bool = True
    DOI_PROVIDER: str = "crossref"  # or datacite

    # DataCite (alternative to Crossref)
    DATACITE_REPOSITORY_ID: Optional[str] = None
    DATACITE_PASSWORD: Optional[str] = None

    # PubMed Central
    PMC_FTP_HOST: str = "ftp.ncbi.nlm.nih.gov"
    PMC_FTP_USER: str
    PMC_FTP_PASSWORD: str
    PMC_FTP_PATH: str = "/upload"

    # Journal Metadata
    JOURNAL_TITLE: str
    JOURNAL_SHORT_TITLE: Optional[str] = None
    JOURNAL_ISSN: str
    JOURNAL_EISSN: str
    JOURNAL_PUBLISHER: str
    JOURNAL_URL: AnyHttpUrl
    JOURNAL_EMAIL: EmailStr

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ORCID
    ORCID_CLIENT_ID: Optional[str] = None
    ORCID_CLIENT_SECRET: Optional[str] = None
    ORCID_API_URL: str = "https://pub.orcid.org/v3.0"

    # Storage
    STORAGE_TYPE: str = "local"  # or s3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: Optional[str] = "us-east-1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
