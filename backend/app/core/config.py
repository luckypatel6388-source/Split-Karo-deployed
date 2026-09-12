from functools import lru_cache
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamic BASE_DIR points to backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Application
    app_name: str = "Split Karo"
    app_version: str = "0.1.0"

    # Environment
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str

    # Security
    secret_key: SecretStr
    access_token_expire_minutes: int = 30

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Authentication cookies
    cookie_name: str = "split_karo_session"
    cookie_secure: bool = False
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"

    # Google OAuth
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# Instantiate settings cleanly without trailing commas
settings = get_settings()


def get_async_database_url() -> str:
    """Return a SQLAlchemy async URL for local and hosted databases."""

    url = settings.database_url.strip()

    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    if url.startswith("mysql://"):
        return "mysql+asyncmy://" + url[len("mysql://") :]
    if url.startswith("mysql+aiomysql://"):
        return "mysql+asyncmy://" + url[len("mysql+aiomysql://") :]

    return url
