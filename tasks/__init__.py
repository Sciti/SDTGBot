from taskiq import TaskiqRedisBroker, TaskiqEvents, TaskiqState
import taskiq_aiogram

from config import settings
from config.log import configure_logging

broker = TaskiqRedisBroker(f"{settings.REDIS_URL}/{settings.TASKIQ_REDIS_DB}")


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    configure_logging()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    ...


taskiq_aiogram.init(broker, "bot:dp", "bot:bot")
