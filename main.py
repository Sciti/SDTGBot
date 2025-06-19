import os
from argparse import ArgumentParser
import asyncio

from config import settings
from config.log import configure_logging


parser = ArgumentParser()
parser.add_argument("-e", "--env_file", default="")
args = parser.parse_args()

if args.env_file:
    os.environ["ENV_FILE"] = args.env_file


if __name__ == "__main__":
    configure_logging()

    from bot import start_bot
    asyncio.run(start_bot(settings.BOT_COMMANDS))
