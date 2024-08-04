import asyncio
import logging
from threading import Thread

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from telethon import TelegramClient

from bot.config import redis, settings
from bot.db.requests import connection_test
from bot.handlers import add_note_router, my_notes_router, startup_router
from bot.menu_commands import set_default_commands
from bot.middlewares.db import DbSessionMiddleware
from bot.notification.send_notification import create_new_loop_for_notification


async def main():
    logging.basicConfig(
        format='[{asctime}] #{levelname:8} {filename}: '
               '{lineno} - {name} - {message}',
        style="{",
        level=logging.INFO,
    )

    bot = Bot(
        token=settings.TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )
    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    async_engine = create_async_engine(settings.get_database_url)
    sessionmaker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    tc = await TelegramClient(
        "bot",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH
    ).start(bot_token=settings.TOKEN)

    async with sessionmaker() as session:
        await connection_test(session)

    dp = Dispatcher(storage=storage)
    dp.update.middleware(middleware=DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_router(startup_router)
    dp.include_router(add_note_router)
    dp.include_router(my_notes_router)

    await set_default_commands(bot=bot)
    await bot.delete_webhook(drop_pending_updates=True)

    global_loop = asyncio.get_event_loop()
    notification_thread = Thread(target=create_new_loop_for_notification, args=(global_loop, tc, sessionmaker))
    notification_thread.start()

    await asyncio.gather(
        dp.start_polling(bot, tc=tc),
        tc.run_until_disconnected(),
    )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt):
        logger.info("Bot stopped")
