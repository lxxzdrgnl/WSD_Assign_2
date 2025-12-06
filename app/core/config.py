from pydantic import model_validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Union, List, Any


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Application Settings
    APP_NAME: str = "Bookstore API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "bookstore"
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="before")
    def assemble_db_connection(cls, v: Any) -> Any:
        if isinstance(v, dict) and "DATABASE_URL" not in v:
            v["DATABASE_URL"] = (
                f"mysql+pymysql://{v.get('DB_USER')}:{v.get('DB_PASSWORD')}"
                f"@{v.get('DB_HOST')}:{v.get('DB_PORT')}/{v.get('DB_NAME')}"
            )
        return v

    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Pagination Defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Bcrypt Settings
    BCRYPT_ROUNDS: int = 12


settings = Settings()
