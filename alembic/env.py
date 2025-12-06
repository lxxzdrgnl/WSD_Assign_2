"""
Alembic Environment Configuration
데이터베이스 마이그레이션 환경 설정
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.database import Base

# 모든 모델 import (Alembic이 테이블을 인식하도록)
from app.models import (
    User, RefreshToken,
    Book, BookView,
    Review, ReviewLike, ReviewLikeCount,
    Comment, CommentLike,
    Cart, Favorite,
    Order, OrderItem,
    Coupon, UserCoupon
)

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 환경 변수에서 데이터베이스 URL 가져오기
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지
        compare_server_default=True,  # 기본값 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경 감지
            compare_server_default=True,  # 기본값 변경 감지
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
