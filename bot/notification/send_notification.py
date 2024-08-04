import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker
from telethon import TelegramClient

from bot.db.notes.requests import NotesDAO


def create_new_loop_for_notification(global_loop, tc: TelegramClient, session_pool: async_sessionmaker):
    asyncio.run_coroutine_threadsafe(notify(tc, session_pool), global_loop)


async def notify(tc: TelegramClient, session_pool: async_sessionmaker):
    while True:
        async with session_pool() as session:
            time_now = datetime.now(tz=timezone(timedelta(hours=3)))
            notes = await NotesDAO.get_notes(session=session)

            for user_telegram_id, text, reminder_time, note_id in notes:
                reminder_time = datetime(
                    year=reminder_time.year,
                    month=reminder_time.month,
                    day=reminder_time.day,
                    hour=reminder_time.hour,
                    minute=reminder_time.minute,
                    tzinfo=timezone(timedelta(hours=3)),
                )

                try:
                    if time_now >= reminder_time:
                        entity = await tc.get_entity(user_telegram_id)
                        await tc.send_message(
                            entity=entity,
                            message=f"⏱Напоминание на {reminder_time}\n\nТекст напоминания:" + text,
                        )
                        await NotesDAO.delete_note(
                            session=session,
                            note_id=note_id,
                        )
                    elif (reminder_time - time_now).seconds in range(540, 600):
                        entity = await tc.get_entity(user_telegram_id)
                        await tc.send_message(
                            entity=entity,
                            message="‼️Уже через 10 минут наступит время твоего уведомления на заметку в "
                                    f"{reminder_time}",
                        )
                except Exception:
                    pass
        await asyncio.sleep(60)
