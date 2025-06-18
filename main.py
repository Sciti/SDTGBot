import asyncio
import datetime
import base64
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, setup_dialogs, StartMode

from bot.dialogs.menu import main_menu_dialog
from bot.dialogs.post import post_dialog
from bot.dialogs.templates import templates_dialog
from bot.dialogs.administration import administration_dialog
from bot.states import MainMenuSG
from database.models import UserRole
from config import settings
from database import async_session_factory
from database.repository import Repository


router = Router()


async def process_code_registration(repo: Repository, message: Message, code: str) -> None:
    code_obj = await repo.get_code(code)
    if not code_obj:
        raise ValueError("Неизвестный код")
    if code_obj.expires_at and code_obj.expires_at < datetime.datetime.utcnow():
        raise ValueError("Срок действия кода истёк")
    if not code_obj.is_active:
        raise ValueError("Код не активен")
    if code_obj.used_count >= code_obj.max_uses:
        raise ValueError("Код уже использован")

    user = await repo.get_user_by_tg_id(message.from_user.id)
    if not user:
        user = await repo.create_user(
            role=UserRole.CLIENT,
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
        )
    else:
        user.role = UserRole.CLIENT
        await repo.update_object(user)

    code_obj.used_count += 1
    code_obj.used_by = user.id
    await repo.update_object(code_obj)


@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    code = message.text.removeprefix("/start").strip()
    async with async_session_factory() as session:
        repo = Repository(session)
        if code:
            try:
                await process_code_registration(repo, message, code)
            except ValueError as err:
                await message.answer(str(err))
                return
        user = await repo.get_user_by_tg_id(message.from_user.id)
        if not user or (
            not code and user.role not in {UserRole.ADMIN, UserRole.MANAGER}
        ):
            return
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(main_menu_dialog)
    dp.include_router(post_dialog)
    dp.include_router(templates_dialog)
    dp.include_router(administration_dialog)
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
