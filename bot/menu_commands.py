from aiogram import types


async def set_default_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="addnote", description="Создать заметку"),
        types.BotCommand(command="mynotes", description="Мои заметки"),
    ])