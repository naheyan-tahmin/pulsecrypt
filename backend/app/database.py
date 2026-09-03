from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None


def get_engine():
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine


def get_session_factory():
    get_engine()
    return SessionLocal


def get_db():
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
