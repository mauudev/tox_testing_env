import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src import use_cases
from src.database import Base, Database, build_async_engine
from src.models.item import ItemNotFound
from src.settings import APP_SETTINGS


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = build_async_engine(
        db_url=APP_SETTINGS.DATABASE_URL_ASYNC,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    title: str
    description: str | None = None


class ItemRes(BaseModel):
    id: int
    title: str
    description: str | None = None


@app.post("/build-item/", response_model=Item)
async def build_item(item: Item):
    return Item(id="foo", **item.model_dump())


@app.post("/items/", response_model=ItemRes)
async def create_item(
    item: Item,
    db_conn: Database = Depends(),
    use_case: use_cases.RegisterItem = Depends(),
):
    try:
        create_command = use_cases.RegisterItemCommand(
            title=item.title,
            description=item.description,
        )
        item = await use_case.handle(command=create_command, db_conn=db_conn)
        return item
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@app.get("/items/{item_id}", response_model=ItemRes)
async def get_item(
    item_id: int,
    db_conn: Database = Depends(),
    use_case: use_cases.GetItem = Depends(),
):
    try:
        read_command = use_cases.GetItemCommand(id=item_id)
        item = await use_case.handle(command=read_command, db_conn=db_conn)
        return item
    except ItemNotFound as e:
        return JSONResponse(status_code=404, content={"message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


def start_server():
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True,
    )


if __name__ == "__main__":
    start_server()
