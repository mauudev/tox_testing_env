from typing import Type

from pydantic import BaseModel

from src.database import Database
from src.models.item import Item


class RegisterItemCommand(BaseModel):
    title: str
    description: str


class ItemRegisteredResponse(BaseModel):
    id: int
    title: str
    description: str


class RegisterItem:
    async def handle(
        self, command: RegisterItemCommand, db_conn: Type[Database]
    ) -> ItemRegisteredResponse:
        print(f"Registering new item for code: {command}")
        async with db_conn.async_db_session() as session:
            new_item = await Item.create(session=session, data=command.model_dump())
            print(f"helooooooyuu")
            await session.commit()
            return ItemRegisteredResponse(**new_item.to_dict())
