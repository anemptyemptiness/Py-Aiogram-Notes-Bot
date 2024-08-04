from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Users


class UsersDAO:
    @classmethod
    async def add_user(
            cls,
            session: AsyncSession,
            name: str,
            email: EmailStr,
            telegram_id: int,
    ):
        stmt = (
            insert(Users)
            .values(
                name=name,
                email=email,
                telegram_id=telegram_id,
            )
        )

        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_user(
            cls,
            session: AsyncSession,
            telegram_id: int,
    ):
        query = (
            select(Users)
            .where(Users.telegram_id == telegram_id)
        )

        result = await session.execute(query)
        return result.scalar()