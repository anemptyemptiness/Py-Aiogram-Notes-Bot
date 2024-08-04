from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Notes, Users


class NotesDAO:
    @classmethod
    async def add_note(
            cls,
            session: AsyncSession,
            text: str,
            reminder_time: datetime,
            user_id: int,
    ):
        user_id = (
            select(Users.id)
            .where(Users.telegram_id == user_id)
            .scalar_subquery()
        )
        stmt = (
            insert(Notes)
            .values(
                text=text,
                reminder_time=reminder_time,
                user_id=user_id,
            )
        )

        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_notes_by_user(
            cls,
            session: AsyncSession,
            user_id: int,
    ):
        query = (
            select(Notes)
            .where(
                Notes.user_id == select(Users.id).where(Users.telegram_id == user_id).scalar_subquery()
            )
            .order_by(Notes.reminder_time)
        )

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_notes(
            cls,
            session: AsyncSession,
    ):
        query = (
            select(
                Users.telegram_id,
                Notes.text,
                Notes.reminder_time,
                Notes.id,
            )
            .join(Users, Users.id == Notes.user_id)
            .order_by(Notes.user_id, Notes.reminder_time)
        )

        result = await session.execute(query)
        return result.all()

    @classmethod
    async def delete_note(
            cls,
            session: AsyncSession,
            note_id: int,
    ):
        stmt = (
            delete(Notes)
            .where(Notes.id == note_id)
        )

        await session.execute(stmt)
        await session.commit()