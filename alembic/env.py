import asyncio
import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Добавляем корень проекта в sys.path для импорта моделей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем Base с метаданными моделей
from app.models.base import Base

# Конфиг Alembic
config = context.config

# Настраиваем логирование из alembic.ini
fileConfig(config.config_file_name)

# Целевые метаданные (для autogenerate)
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в офлайн-режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Выполнение миграций с уже подключённой БД"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в онлайне с async движком"""
    connectable = create_async_engine(
        config.get_section(config.config_ini_section)["sqlalchemy.url"],
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())