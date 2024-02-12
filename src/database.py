import os
from asyncio import current_task
from contextlib import asynccontextmanager, contextmanager
from functools import cache
from typing import AsyncIterator, Callable, Iterator

from sqlalchemy import MetaData, QueuePool
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from src.settings import APP_SETTINGS

ENV = os.environ.get("ENV", False)
POOL_CONFIG = {
    "local": {
        "poolclass": QueuePool,
        "pool_size": int(APP_SETTINGS.DATABASE_POOL_SIZE),
    },
    "docker": {
        "poolclass": QueuePool,
        "pool_size": int(APP_SETTINGS.DATABASE_POOL_SIZE),
    },
    "test": {"poolclass": NullPool},
}

pool_config = lambda: POOL_CONFIG.get(ENV, POOL_CONFIG["local"])


@cache
def build_engine(
    db_url: str = APP_SETTINGS.DATABASE_URL,
) -> Engine:
    return create_engine(
        db_url,
        **pool_config(),
    )


@cache
def build_async_engine(
    db_url: str = APP_SETTINGS.DATABASE_URL_ASYNC,
) -> Engine:
    return create_async_engine(
        db_url,
        **pool_config(),
    )


@cache
def sync_session_factory(
    db_url: str = APP_SETTINGS.DATABASE_URL,
) -> Callable[[], Session]:
    return scoped_session(
        sessionmaker(bind=build_engine(db_url), autocommit=False, autoflush=True)
    )


@cache
def async_session_factory(
    db_url: str = APP_SETTINGS.DATABASE_URL_ASYNC,
) -> Callable[[], AsyncSession]:
    AsyncScopedSession = async_scoped_session(
        async_sessionmaker(
            bind=build_async_engine(db_url),
            autocommit=False,
            autoflush=True,
            future=True,
            expire_on_commit=False,
        ),
        scopefunc=current_task,
    )
    return AsyncScopedSession


@contextmanager
def db_session(
    db_url: str = APP_SETTINGS.DATABASE_URL,
) -> Iterator[Session]:
    session: Session = sync_session_factory(db_url)()
    try:
        yield session

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


@asynccontextmanager
async def async_db_session(
    db_url: str = APP_SETTINGS.DATABASE_URL_ASYNC,
) -> AsyncIterator[AsyncSession]:
    session: AsyncSession = async_session_factory(db_url)()
    try:
        yield session

    except Exception as e:
        print("Database error, rolling back ..")
        await session.rollback()
        raise e

    finally:
        print("Closing DB session ..")
        await session.close()


class Database:

    def __init__(
        self,
        db_url: str = APP_SETTINGS.DATABASE_URL,
        async_db_url: str = APP_SETTINGS.DATABASE_URL_ASYNC,
    ) -> None:
        self._sync_session_factory = sync_session_factory
        self._async_session_factory = async_session_factory
        self._db_url = db_url
        self._async_db_url = async_db_url

    @contextmanager
    def db_session(self) -> Iterator[Session]:
        session: Session = self._sync_session_factory(self._db_url)()
        try:
            yield session

        except Exception as e:
            session.rollback()
            raise e

        finally:
            print("Closing DB session ..")
            session.close()

    @asynccontextmanager
    async def async_db_session(self) -> AsyncIterator[AsyncSession]:
        session: AsyncSession = self._async_session_factory(self._async_db_url)()
        try:
            yield session

        except Exception as e:
            print("Database error, rolling back ..")
            await session.rollback()
            raise e

        finally:
            print("Closing DB session ..")
            await session.close()


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=convention)  # type: ignore
