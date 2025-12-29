from typing import Generator

from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _create_engine_and_session():
    sqlalchemy_database_url = settings.DATABASE_URL

    # When using in-memory SQLite, we need StaticPool to share the same
    # in-memory database across all threads, and check_same_thread=False
    # to allow FastAPI's thread pool to access it.
    if sqlalchemy_database_url == "sqlite://":
        engine = create_engine(
            sqlalchemy_database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(sqlalchemy_database_url)

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session_local


engine, SessionLocal = _create_engine_and_session()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
