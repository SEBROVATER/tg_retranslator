# ruff: noqa: RUF029, S403, S301
import asyncio
import os
import pickle

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.link_preview_options import LinkPreviewOptions
from aiogram.utils.formatting import Code
from dotenv import load_dotenv
from redis import Redis

from general_utils.loggers import LOGGER

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
RECEIVERS = {int(user) for user in os.getenv("RECEIVERS").split(",")}

shutdown_event = asyncio.Event()

redis = Redis(
    host="redis",
    port=6379,
    db=0,
    username=os.getenv("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSWORD"),
)
if not redis.ping():
    msg = "Can't connect to Redis"
    raise ConnectionError(msg)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("id"))
async def my_id(message: Message) -> None:
    await message.reply(**Code(message.chat.id).as_kwargs())


@dp.shutdown()
async def shutdown() -> None:
    LOGGER.info("Shutting down bot...")
    shutdown_event.set()


async def periodic_task() -> None:
    try:
        while not shutdown_event.is_set():
            msg = redis.rpop("TG.MESSAGES")
            if msg is not None:
                try:
                    msg = pickle.loads(msg)
                    LOGGER.info(f"Retranslate message: {msg.as_pretty_string()}")
                    for receiver in RECEIVERS:
                        await bot.send_message(receiver, **msg.as_kwargs(),
                                               link_preview_options=LinkPreviewOptions(is_disabled=True))
                except pickle.UnpicklingError:
                    LOGGER.warning(f"Couldn't unpickle message: {msg.decode('utf-8')}")
                    for receiver in RECEIVERS:
                        await bot.send_message(receiver, msg.decode("utf-8"),
                                               link_preview_options=LinkPreviewOptions(is_disabled=True))
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        LOGGER.info("Periodic task cancelled")


background_task = set()


async def main() -> None:
    task = asyncio.create_task(periodic_task())
    background_task.add(task)
    task.add_done_callback(background_task.discard)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
