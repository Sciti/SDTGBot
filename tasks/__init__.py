from __future__ import annotations

import datetime
from typing import List
from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from config import settings
from config.log import configure_logging
from database import repository as repo
from database.models import Post, Channel


scheduler = AsyncIOScheduler()
logger = getLogger("tasks")


def start_scheduler() -> None:
    """Start APScheduler with configured logging."""
    configure_logging()
    if not scheduler.running:
        scheduler.start()


async def send_post(post_id: int, bot: Bot) -> None:
    """Send post text to selected channels."""
    post: Post = await repo.get_post(post_id)
    if not post:
        return

    markup = []
    if post.use_default_buttons and post.steam_id:
        markup.extend(
            InlineKeyboardButton(
                text=text,
                url=url.format(app_id=post.steam_id),
                callback_data=f"link_{text.lower()}:{post.steam_id}",
            )
            for text, url in settings.POST_BUTTONS.items()
        )
    if post.buttons:
        markup.extend(
            InlineKeyboardButton(text=b["text"], url=b["url"]) for b in post.buttons
        )

    channels: List[Channel] = await repo.get_post_channels(post_id)
    for channel in channels:
        keyboard = InlineKeyboardBuilder(markup=[markup])
        keyboard.adjust(3)
        try:
            if post.tg_image_id:
                msg = await bot.send_photo(
                    channel.channel_id,
                    post.tg_image_id,
                    caption=post.text,
                    parse_mode="HTML",
                    show_caption_above_media=post.caption_above,
                    reply_markup=keyboard.as_markup(),
                )
            else:
                msg = await bot.send_message(
                    channel.channel_id,
                    post.text,
                    parse_mode="HTML",
                    reply_markup=keyboard.as_markup(),
                )
        except TelegramBadRequest as e:
            logger.error(e, exc_info=True)
            await bot.send_message(
                post.author.tg_id,
                f"Ошибка отправки поста в канал {channel.channel_name}:\n{e}",
            )
            return
        
        if msg:
            await repo.mark_post_sent(post.id, msg.message_id)


def schedule_post(send_time: datetime.datetime, post_id: int, bot: Bot) -> None:
    """Schedule post sending at a specific datetime."""
    trigger = DateTrigger(run_date=send_time)
    scheduler.add_job(send_post, trigger, args=(post_id, bot))


__all__ = ["scheduler", "start_scheduler", "schedule_post", "send_post"]
