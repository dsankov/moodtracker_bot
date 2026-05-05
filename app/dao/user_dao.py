from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.dao.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO:
    @staticmethod
    async def upsert_user(
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        last_name: str | None,
        username: str | None,
    ) -> User:
        stmt = insert(User).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "username": stmt.excluded.username,
                "last_seen_at": stmt.excluded.last_seen_at,
            },
        )
        await session.execute(stmt)
        await session.commit()
        # Fetch the user to return
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update_language(
        session: AsyncSession,
        telegram_id: int,
        language: str,
    ) -> None:
        """Update the user's language preference."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language=language)
        )
        await session.execute(stmt)
        await session.commit()
