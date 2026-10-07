"""Подключение к базе данных SQLite через SQLAlchemy.

Модуль создаёт движок, фабрику сессий и функцию инициализации БД.
"""
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src import config
from src.db.models import Base

# Движок SQLite: файл studio.db в корне проекта.
# echo=False — не выводить SQL в консоль (можно поставить True для отладки).
engine = create_engine(f"sqlite:///{config.DB_PATH}", echo=False, future=True)

# Фабрика сессий: каждая сессия — отдельная транзакция.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Создаёт все таблицы в БД, если их ещё нет."""
    Base.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Контекстный менеджер для работы с сессией БД.

    Автоматически закрывает сессию после выхода из блока ``with``.

    Yields:
        Session: Активная сессия SQLAlchemy.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()