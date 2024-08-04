from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient

from bot.db.notes.requests import NotesDAO
from bot.fsm.fsm import AddNoteSG
from bot.lexicon.lexicon import MONTH_DAYS

router = Router(name="add_note_router")


@router.message(Command(commands=["addnote"]), StateFilter(default_state))
async def process_add_note_command(message: Message, state: FSMContext):
    await message.answer("Введите текст для заметки📝")
    await state.set_state(AddNoteSG.text)


@router.message(StateFilter(AddNoteSG.text), F.text)
async def process_add_note_text_command(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        text=f"Текст заметки: {message.text}\n"
             "А теперь введи время напоминания заметки, чтобы я вовремя напомнил тебе о планах!\n\n"
             "<em>Например: 13:37</em>",
    )
    await state.set_state(AddNoteSG.custom_time)


@router.message(StateFilter(AddNoteSG.custom_time), F.text)
async def process_add_note_custom_time_command(message: Message, state: FSMContext):
    if len(message.text.split(":")) == 2:
        hour, minutes = message.text.split(":")

        if int(hour) < 0 or int(hour) > 23:
            await message.answer(
                text="Вы ввели некорректный час!\n\n"
                     "Я ожидаю от тебя число от 0 до 23!"
            )
        elif int(minutes) < 0 or int(minutes) > 59:
            await message.answer(
                text="Вы ввели некорректные минуты!\n\n"
                     "Я ожидаю от тебя число от 0 до 59!"
            )
        else:
            await state.update_data(custom_hour=int(hour))
            await state.update_data(custom_minutes=int(minutes))
            await message.answer(
                text="Отлично! Теперь введи дату, когда мне нужно будет уведомить тебя "
                     "в формате <b>ГГГГ-ММ-ДД</b>\n\n"
                     "<em>Например: 2024-01-01 (1 января 2024 года)</em>"
            )
            await state.set_state(AddNoteSG.custom_date)
    else:
        await message.answer(
            text="Вы ввели некорректное время!\n\n"
                 "Я ожидаю от тебя время в формате <em><b>час:минуты</b></em>\n"
                 "<em>Например: 13:37</em>"
        )


@router.message(StateFilter(AddNoteSG.custom_date), F.text)
async def process_add_note_custom_date_command(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        tc: TelegramClient,
):
    if len(message.text.split("-")) == 3:
        year, month, day = message.text.split("-")
        time_now = datetime.utcnow()

        if int(year) < time_now.year or int(year) > time_now.year + 1:
            await message.answer(
                text="Введенный год не может быть меньше или больше текущего на 1 год!",
            )
        elif int(month) < time_now.month or int(month) > 12:
            await message.answer(
                text="Введенный месяц не может быть меньше текущего или больше количества существующих месяцев (12)!",
            )
        elif int(day) < time_now.day or int(day) > MONTH_DAYS[int(month)]:
            await message.answer(
                text="Введенный день не может быть меньше текущего или больше количества дней в указанном месяце!",
            )
        else:
            data = await state.get_data()

            try:
                reminder_time = datetime(
                    year=int(year),
                    month=int(month),
                    day=int(day),
                    hour=data.get("custom_hour"),
                    minute=data.get("custom_minutes"),
                )
                await NotesDAO.add_note(
                    session=session,
                    text=data.get("text"),
                    reminder_time=reminder_time,
                    user_id=message.from_user.id,
                )

                await message.answer(
                    text="Отлично! Я сохранил заметку себе✅"
                )
                await message.answer(
                    text="/addnote - создать еще одну заметку\n"
                         "/mynotes - посмотреть свои заметки"
                )
                await state.clear()
            except Exception:
                await message.answer(
                    text="Произошла ошибка!\n"
                         "Пожалуйста, проверь корректность введенного времени и давай начнем сначала",
                )
                await state.clear()
                await state.set_state(AddNoteSG.custom_time)
                await state.update_data(text=data.get("text"))
                await message.answer(
                    text=f"Текст заметки: {message.text}\n"
                         "Введи новое время заметки, чтобы я напомнил тебе о планах!\n\n"
                         "<em>Например: 13:37</em>",
                )
    else:
        await message.answer(
            text="Вы ввели некорректную дату!\n\n"
                 "Я ожидаю от тебя дату в формате <b>ГГГГ-ММ-ДД</b>\n"
                 "<em>Например: 2024-01-01 (1 января 2024 года)</em>",
        )
