import hashlib
import logging
import os
from random import choice
from typing import List

from aiogram import Bot, Dispatcher, executor
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
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

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

AVAILABLE_GROUP_COMMANDS = ["/random", "/выборка", "/"]
cock_controller = CockController()


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):

    user = inline_query.from_user

    greeting_name = user.first_name or "Unknown"
    greeting_surname = user.last_name or "Unknown"
    cock_size = cock_controller.get(user.id)

    result_string = f"{greeting_name} {greeting_surname}, your cock is {cock_size} cm"
    input_content = types.InputTextMessageContent(result_string)

    result_id: str = hashlib.md5(user.username.encode()).hexdigest()
    item = types.InlineQueryResultArticle(
        id=result_id,
        title=f'Check size',
        input_message_content=input_content,
    )

    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=0, is_personal=True)


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


if __name__ == "__main__":
    while True:
        executor.start_polling(dp, skip_updates=True)
