from aiogram import Bot
from taskiq import TaskiqEvents, TaskiqState, TaskiqScheduler, TaskiqDepends
from taskiq_redis import (
    RedisAsyncResultBackend,
    ListQueueBroker,
    RedisScheduleSource,
)
import taskiq_aiogram
from database import repository as repo

from config import settings
from config.log import configure_logging

redis_url = f"{settings.REDIS_URL}/{settings.TASKIQ_REDIS_DB}"
result_backend = RedisAsyncResultBackend(redis_url, result_ex_time=1000)
broker = ListQueueBroker(redis_url).with_result_backend(result_backend)
redis_source = RedisScheduleSource(redis_url)
scheduler = TaskiqScheduler(broker, sources=[redis_source])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    configure_logging()
    await redis_source.startup()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    await redis_source.shutdown()


taskiq_aiogram.init(broker, "bot:dp", "bot:bot")


@broker.task
async def send_post(post_id: int, bot: Bot = TaskiqDepends()) -> None:
    """Send post text to selected channels."""
    post = await repo.get_post(post_id)
    if not post:
        return
    channels = await repo.get_post_channels(post_id)
    for channel in channels:
        msg = await bot.send_message(channel.channel_id, post.text)
    if channels:
        await repo.mark_post_sent(post.id, msg.message_id)


__all__ = ["broker", "send_post", "redis_source"]
