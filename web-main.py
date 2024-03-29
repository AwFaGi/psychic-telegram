import asyncio
import hashlib
import logging
import os
from random import choice
from typing import List

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram_media_group import MediaGroupFilter, media_group_handler
from dotenv import load_dotenv

from cock_controller import CockController
from commands import bot_commands

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TG_BOT_TOKEN", None)
if not TOKEN:
    logging.log(logging.ERROR, 'Set "TG_BOT_TOKEN"')
    raise SystemExit

API_TOKEN = 'BOT TOKEN HERE'

# webhook settings
WEBHOOK_HOST = 'https://awfagi.pythonanywhere.com/'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 80

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
dp = Dispatcher(bot)

AVAILABLE_GROUP_COMMANDS = ["/random", "/выборка", "/"]
cock_controller = CockController()


@dp.message_handler(commands=bot_commands.keys())
async def process(message: types.Message):
    command = message.get_command()[1:]
    await bot_commands[command][0](message)


@dp.message_handler(commands="start")
async def start_func(message: types.Message):
    await message.answer("Привет! Я помогу тебе сделать выбор в трудной ситуации. Попробуй написать /help")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def master(message: types.Message):
    if message.chat.type == "private":
        await message.reply(choice(message.text.splitlines()))
    elif message.chat.type == "group":
        cash = message.text.splitlines()
        if cash[0] in AVAILABLE_GROUP_COMMANDS and len(cash) > 1:
            await message.reply(choice(cash[1:]))
        elif cash[0] in AVAILABLE_GROUP_COMMANDS:
            await message.reply("Мне нужны варианты!")


@dp.message_handler(MediaGroupFilter(), content_types=types.ContentType.PHOTO)
@media_group_handler
async def album_handler(messages: List[types.Message]):
    msg = choice(messages)
    await msg.reply_photo(msg.photo[-1].file_id)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def album_handler(message: types.Message):
    await message.reply_photo(message.photo[-1].file_id)


@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_type(message: types.Message):
    await message.reply("Извини, я пока не могу с таким работать. Попробуй /help")


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    # insert code here to run it before shutdown
    pass


if __name__ == '__main__':
    start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown,
                  skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT)