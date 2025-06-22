from __future__ import annotations

import datetime
from logging import getLogger

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram_dialog import DialogManager, setup_dialogs, StartMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.dialogs.menu import main_menu_dialog
from bot.dialogs.post import dialog as post_dialog
from bot.dialogs.templates import templates_dialog
from bot.dialogs.administration import administration_dialog
from bot.states import MainMenuSG
from database.models import UserRole
from database import redis as redis_connection
from database import repository as repo
from config import settings
from tasks import broker as taskiq_broker


logger = getLogger("bot")

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode='HTML'
    )
)
key_builder = DefaultKeyBuilder(prefix="sdtg", with_destiny=True)
storage = RedisStorage(redis_connection, key_builder)
dp = Dispatcher(storage=storage)

main_router = Router()
dialogs_router = Router()


async def process_code_registration(message: Message, code: str) -> None:
    code_obj = await repo.get_code(code)
    if not code_obj:
        raise ValueError("Неизвестный код")
    if code_obj.expires_at and code_obj.expires_at < datetime.datetime.now(code_obj.expires_at.tzinfo):
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


@main_router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    code = message.text.removeprefix("/start").strip()
    if code:
        try:
            await process_code_registration(message, code)
        except ValueError as err:
            await message.answer(str(err))
            return
    user = await repo.get_user_by_tg_id(message.from_user.id)
    if not user or (
        not code and user.role not in {UserRole.ADMIN, UserRole.MANAGER}
    ):
        return
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)

@main_router.message(F.is_automatic_forward)
async def process_auto_forward(message: Message, state: FSMContext):
    markup = message.reply_markup.inline_keyboard
    comments_button = InlineKeyboardButton(
        text="Комментарии",
        url=f"https://t.me/c/{message.chat.shifted_id}/{message.message_id + 1000000}?thread={message.message_id}",
        callback_data=f"comments_{message.message_id}"
    )
    markup.append([comments_button, ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_reply_markup(
        chat_id=message.forward_from_chat.id,
        message_id=message.forward_from_message_id,
        reply_markup=keyboard
    )


@dp.startup()
async def setup_taskiq(bot: Bot, *_args, **_kwargs):
    if not taskiq_broker.is_worker_process:
        logger.info("Setting up taskiq")
        await taskiq_broker.startup()


@dp.shutdown()
async def shutdown_taskiq(bot: Bot, *_args, **_kwargs):
    if not taskiq_broker.is_worker_process:
        logger.info("Shutting down taskiq")
        await taskiq_broker.shutdown()


async def start_bot(commands: dict[str, str] | None = None) -> None:
    dialogs_router.include_routers(
        main_menu_dialog,
        post_dialog,
        templates_dialog,
        administration_dialog
    )
    main_router.include_router(dialogs_router)

    dp.include_router(main_router)
  
    setup_dialogs(dp)

    if commands:
        await bot.set_my_commands(
            [BotCommand(command=cmd, description=desc) for cmd, desc in commands.items()]
        )

    await dp.start_polling(bot)

