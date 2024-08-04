import re

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import StartupSG

router = Router(name="startup_router")


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    user = await UsersDAO.get_user(
        session=session,
        telegram_id=message.from_user.id
    )

    if not user:
        await message.answer(
            text="😔 Ой, кажется ты не зарегистрирован!\n"
                 "Тебе нужно придумать себе логин и почту, после чего отправь их сюда!\n\n"
                 "<em>Например: <b>твой_логин</b> <b>твоя@почта.тут</b></em>"
        )
        await state.set_state(StartupSG.register)
    else:
        await message.answer(
            text=f"Привет, <b>{user.name}</b>!\n\n"
                 "/addnote - чтобы создать заметку\n"
                 "/mynotes - чтобы посмотреть свои заметки"
        )


@router.message(StateFilter(StartupSG.register), F.text)
async def process_registration_command(message: Message, state: FSMContext, session: AsyncSession):
    if len(message.text.split()) == 2:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        try:
            name, email = message.text.split()
            if not re.fullmatch(regex, email):
                await message.answer(
                    text="Неправильный формат почты! Пожалуйста, используй корректный почтовый адрес\n\n"
                         "<em>Например: <b>твоя@почта.тут</b></em>",
                )
                return

            await UsersDAO.add_user(
                session=session,
                name=name,
                email=email,
                telegram_id=message.from_user.id,
            )
            await message.answer(
                text=f"Супер! Теперь я запомнил тебя, {name}😊\n\n"
                     "/addnote - чтобы создать заметку\n"
                     "/mynotes - чтобы посмотреть свои заметки"
            )
            await state.clear()
        except Exception:
            await message.answer(
                text="🤔 Кажется, в введенных данных есть что-то некорректное...\n"
                     "Попробуй перепроверить их и ввести заново!",
            )
    else:
        await message.answer(
            text="Кажется, ты прислал немного больше данных, чем нужно...\n"
                 "Я ожидаю от тебя имя и email\n\n"
                 "<em>Например: <b>твой_логин</b> <b>твоя@почта.тут</b></em>",
        )


@router.message(StateFilter(StartupSG.register))
async def warning_registration_command(message: Message):
    await message.answer(
        text="Это не похоже на текст...\n"
             "Я ожидаю от тебя имя и email\n\n"
             "<em>Например: <b>твой_логин</b> <b>твоя@почта.тут</b></em>",
    )