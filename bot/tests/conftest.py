import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from bot.config import settings
from bot.handlers import add_note_router, my_notes_router, startup_router
from bot.middlewares.db import DbSessionMiddleware
from bot.tests.mocked_aiogram import MockedBot, MockedSession


@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot


@pytest.fixture(scope="session")
def engine():
    eng: AsyncEngine = create_async_engine(url=settings.get_database_url)
    yield eng
    eng.sync_engine.dispose()


@pytest.fixture(scope="session")
def dp(engine) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
    dispatcher.update.middleware(middleware=DbSessionMiddleware(session_pool=sessionmaker))
    dispatcher.include_routers(
        startup_router,
        add_note_router,
        my_notes_router,
    )
    return dispatcher


@pytest_asyncio.fixture(scope="function")
async def session(engine):
    async with AsyncSession(engine) as s:
        yield s