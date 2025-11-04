from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 프로젝트 모듈 import를 위한 경로 설정
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# SQLModel 메타데이터와 DATABASE_URL 가져오기
from sqlmodel import SQLModel
from database import DATABASE_URL
from models import User  # 모든 모델을 import해야 메타데이터에 포함됨
from analysis_models import AnalysisRecord  # 분석 결과 테이블

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 실제 DATABASE_URL로 덮어쓰기 (alembic.ini의 값 대신)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (비동기 버전).

    비동기 SQLAlchemy 엔진을 사용하여 마이그레이션을 실행합니다.
    """
    
    async def do_run_migrations():
        """비동기 마이그레이션 실행."""
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations_sync)

        await connectable.dispose()

    def do_run_migrations_sync(connection):
        """동기 컨텍스트에서 마이그레이션 실행."""
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경 감지
        )

        with context.begin_transaction():
            context.run_migrations()

    # asyncio 이벤트 루프에서 실행
    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
