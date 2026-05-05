from __future__ import annotations

import uuid
from datetime import datetime  # noqa: TC003

from sqlalchemy import TIMESTAMP, BigInteger, Boolean, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.dao.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(5), server_default="en")
    first_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserActivity(Base):
    __tablename__ = "user_activities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    activity_type: Mapped[str] = mapped_column(String(50))
    command: Mapped[str | None] = mapped_column(String(100), nullable=True)
    callback_data: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text_preview: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Emotion(Base):
    __tablename__ = "emotions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
