from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from bot.db.base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)


class Notes(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    reminder_time: Mapped[datetime] = mapped_column(TIMESTAMP)