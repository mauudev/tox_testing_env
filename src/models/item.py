from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ItemError(Exception):
    pass


class ItemAlreadyExists(ItemError):
    pass


class ItemNotFound(ItemError):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True
    )
    title: Mapped[str] = mapped_column(nullable=True, default=None)
    description: Mapped[str] = mapped_column(nullable=True, default=None)

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, title={self.title!r}, description={self.description!r})"

    @classmethod
    async def create(cls, session: AsyncSession, data: dict) -> Item:
        try:
            item = Item(**data)
            session.add(item)
            await session.flush()
            return item
        except ItemAlreadyExists:
            raise
        except SQLAlchemyError as e:
            raise ItemError(f"Failed to create Item: {str(e)}")

    @classmethod
    async def read_by_id(cls, session: AsyncSession, _id: int) -> Item | None:
        try:
            stmt = select(cls).where(cls.id == _id)
            item = await session.scalar(stmt.order_by(cls.id))
            if not item:
                raise ItemNotFound(f"Item, with id [{_id}] not found")
            return item
        except SQLAlchemyError as e:
            raise ItemError(f"Failed to read Item with id: [{_id}] -> {str(e)}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }
