from bot.handlers.user_handlers.add_note import router as add_note_router
from bot.handlers.user_handlers.my_notes import router as my_notes_router
from bot.handlers.user_handlers.startup import router as startup_router

__all__ = [
    "startup_router",
    "add_note_router",
    "my_notes_router",
]