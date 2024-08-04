from datetime import datetime

import pytest
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.types import Chat, Message, Update, User
from sqlalchemy import select

from bot.db.models import Users


def make_message(user_id: int, text: str) -> Message:
    user = User(id=user_id, first_name="User", is_bot=False)
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    return Message(message_id=1, from_user=user, chat=chat, date=datetime.now(), text=text)


@pytest.mark.asyncio
async def test_start_command(dp, bot, session):
    user_id = 1234567
    flow_messages = [
        make_message(user_id, "/start"),
        make_message(user_id, "anempty test@mail.ru")
    ]

    for message in flow_messages:
        bot.add_result_for(method=SendMessage, ok=True)
        await dp.feed_update(bot, Update(message=message, update_id=1))

    stmt = select(Users).where(Users.telegram_id == user_id)
    user_response = await session.scalar(stmt)
    assert user_response is not None
    assert user_response.telegram_id == user_id
