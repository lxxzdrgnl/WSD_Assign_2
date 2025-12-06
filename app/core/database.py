"""
Database Configuration
SQLAlchemy 데이터베이스 연결 및 세션 관리
"""
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# 데이터베이스 URL
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy 엔진 생성
engine: Engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # SQL 로그 출력 (개발 시 True)
)

# 세션 팩토리
SessionLocal: type[sessionmaker] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()


def get_db():
    """
    데이터베이스 세션 의존성
    FastAPI 엔드포인트에서 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
