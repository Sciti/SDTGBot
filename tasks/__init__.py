from taskiq import TaskiqEvents, TaskiqState
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker, ListQueueBroker
import taskiq_aiogram

from config import settings
from config.log import configure_logging

redis_url = f"{settings.REDIS_URL}/{settings.TASKIQ_REDIS_DB}"
result_backend = RedisAsyncResultBackend(redis_url, result_ex_time=1000)
broker = ListQueueBroker(redis_url).with_result_backend(result_backend)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    configure_logging()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    ...


taskiq_aiogram.init(broker, "bot:dp", "bot:bot")
