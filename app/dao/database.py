import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import TIMESTAMP, func, inspect
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(url=settings.DB_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(),
    )

    def to_dict(self, exclude_none: bool = False):
        """Convert the model to a dictionary."""
        data = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)
            if exclude_none and value is None:
                continue

            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            data[column.key] = value
        return data
