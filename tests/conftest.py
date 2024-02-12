from typing import AsyncIterator

import pytest
from httpx import AsyncClient

from src.api.main import app as fastapi_app
from src.database import Base, Database, build_async_engine, build_engine
from src.settings import APP_SETTINGS


def pytest_collectreport(report):
    print(f"DATABASE_URL_ASYNC: {APP_SETTINGS.DATABASE_URL_ASYNC}")
    print("CONFTEST loaded !")


@pytest.fixture(params=["asyncio"], scope="session")
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="module")
async def async_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=fastapi_app, base_url="http://localhost") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
async def test_db():
    engine = build_async_engine(
        db_url=APP_SETTINGS.DATABASE_URL_ASYNC,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# @pytest.fixture(scope="module", autouse=True)
# def test_db():
#     engine = build_engine(db_url=TESTING_DATABASE_URL, pool_size=DATABASE_POOL_SIZE)
#     Base.metadata.create_all(engine)
#     yield
# Base.metadata.drop_all(engine)


@pytest.fixture
async def db_conn() -> Database:
    return Database(APP_SETTINGS.DATABASE_URL_ASYNC)
