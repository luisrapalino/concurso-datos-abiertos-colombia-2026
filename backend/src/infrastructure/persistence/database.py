from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def init_engine(database_url: str) -> None:
    global _engine, _session_factory
    if _engine is not None:
        return
    _engine = create_engine(database_url, pool_pre_ping=True)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def get_engine() -> Engine:
    if _engine is None:
        msg = "Database engine is not initialized. Call init_engine() during application startup."
        raise RuntimeError(msg)
    return _engine


def get_session() -> Generator[Session, None, None]:
    if _session_factory is None:
        msg = "Database session factory is not initialized. Call init_engine() during application startup."
        raise RuntimeError(msg)
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
