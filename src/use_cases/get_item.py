from typing import Type

from pydantic import BaseModel

from src.database import Database
from src.models.item import Item


class GetItemCommand(BaseModel):
    id: int


class GetItemResponse(BaseModel):
    id: int
    title: str
    description: str


class GetItem:
    async def handle(
        self, command: GetItemCommand, db_conn: Type[Database]
    ) -> GetItemResponse:
        print(f"Getting item for id: {command.id}")
        async with db_conn.async_db_session() as session:
            item = await Item.read_by_id(session=session, _id=command.id)
            await session.commit()
            return GetItemResponse(**item.to_dict())
