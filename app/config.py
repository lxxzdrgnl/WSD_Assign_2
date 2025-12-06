"""
Application Configuration
환경 변수를 로드하고 설정을 관리합니다.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Application
    APP_NAME: str = "Bookstore API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy 데이터베이스 URL 생성"""
        # 개발용: SQLite (파일 기반 - 데이터 유지됨)
        if self.ENVIRONMENT == "development":
            return "sqlite:///./bookstore.db"

        # 프로덕션: MySQL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Bcrypt
    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스를 캐시하여 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
