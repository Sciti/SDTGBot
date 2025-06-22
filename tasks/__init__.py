from __future__ import annotations

import datetime
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings
from config.log import configure_logging
from database import repository as repo
from database.models import Post, Channel


scheduler = AsyncIOScheduler()


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

    markup = [
        InlineKeyboardButton(
            text=text,
            url=url.format(app_id=post.steam_id),
            callback_data=f"link_{text.lower()}:{post.steam_id}",
        )
        for text, url in settings.POST_BUTTONS.items()
    ]
    channels: List[Channel] = await repo.get_post_channels(post_id)
    for channel in channels:
        keyboard = InlineKeyboardBuilder(markup=[markup])
        if post.tg_image_id:
            msg = await bot.send_photo(
                channel.channel_id,
                post.tg_image_id,
                caption=post.text,
                parse_mode="HTML",
                reply_markup=keyboard.as_markup(),
            )
        else:
            msg = await bot.send_message(
                channel.channel_id,
                post.text,
                parse_mode="HTML",
                reply_markup=keyboard.as_markup(),
            )
        if msg:
            await repo.mark_post_sent(post.id, msg.message_id)


def schedule_post(send_time: datetime.datetime, post_id: int, bot: Bot) -> None:
    """Schedule post sending at a specific datetime."""
    trigger = DateTrigger(run_date=send_time)
    scheduler.add_job(send_post, trigger, args=(post_id, bot))


__all__ = ["scheduler", "start_scheduler", "schedule_post", "send_post"]
