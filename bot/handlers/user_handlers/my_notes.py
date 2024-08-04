import asyncio

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.notes.requests import NotesDAO

router = Router(name="my_notes_router")


@router.message(Command(commands=["mynotes"]), StateFilter(default_state))
async def process_my_notes_command(message: Message, session: AsyncSession):
    my_notes = await NotesDAO.get_notes_by_user(
        session=session,
        user_id=message.from_user.id,
    )
    if my_notes:
        counter = 0

        for note in my_notes:
            if counter == 19:
                await asyncio.sleep(1)
            await message.answer(
                text=f"⏳<b>Время напоминания</b>: <em>{note.reminder_time}</em>\n"
                     f"📝<b>Текст</b>: <em>{note.text}</em>"
            )
            counter += 1
    else:
        await message.answer(
            text="У вас <b>нет</b> ни одной заметки!\n"
                 "/addnote - чтобы добавить заметку"
        )
