import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from typing import List
from random import choice, randrange, betavariate
import os
import datetime
import hashlib
from aiogram_media_group import MediaGroupFilter, media_group_handler
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TG_BOT_TOKEN", None)
if not TOKEN:
    logging.log(logging.ERROR, 'Set "TG_BOT_TOKEN"')
    raise SystemExit

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    d = int(betavariate(alpha=2, beta=5) * 50)
    greeting_name, greeting_surname = (inline_query.from_user.first_name or "Unknown"), (inline_query.from_user.last_name or "Unknown")
    input_content = types.InputTextMessageContent(f"{greeting_name} {greeting_surname}, your cock is {d} cm")
    result_id: str = hashlib.md5(inline_query.from_user.username.encode()).hexdigest()
    item = types.InlineQueryResultArticle(
        id=result_id,
        title=f'Check size',
        input_message_content=input_content,
    )
    dt = datetime.datetime.now()
    cache_time = ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=cache_time, is_personal=True)

async def help_func(message: types.Message):
    s = "Для выбора текстовых значений, напиши их по одному в строке.\nДля выбора фотографий, отправь их в одном сообщении\n" + \
        "\n".join([f"<i>/{i}:</i> {bot_commands[i][1]}" for i in bot_commands.keys()])
    await message.answer(s, parse_mode="HTML")

async def dice_func(message: types.Message):
    await message.reply_dice()

async def range_func(message: types.Message):
    try:
        s = list(map(int, message.get_args().split()))
        if len(s) == 0:
            await message.reply( randrange(1, 101) )
        else:
            await message.reply( randrange(*s) )
    except Exception as e: 
        await message.reply("Произошла ошибка!")

bot_commands = {
    "help": (help_func, "Пишет данную справку."),
    "dice": (dice_func, "Бросает кубик."),
    "range": (range_func, "Принимает до 3 целых чисел: \
        <code>\nконец\nначало конец\nначало конец шаг\n</code>Возвращает целое число из указанного промежутка.\
        По умолчанию: <i><code>/range 1 100</code></i>")
}

@dp.message_handler(commands=bot_commands.keys())
async def process(message: types.Message):
    await bot_commands[message.get_command()[1:]][0](message)

@dp.message_handler(commands="start")
async def start_func(message: types.Message):
    await message.answer("Привет! Я помогу тебе сделать выбор в трудной ситуации. Попробуй написать /help")

AVAILABLE_GROUP_COMMANDS = ["/random", "/выборка", "/"]
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def master(message: types.Message):
    if message.chat.type == "private":
        await message.reply( choice( message.text.splitlines() ) )
    elif message.chat.type == "group":
        cash = message.text.splitlines()
        if cash [0] in AVAILABLE_GROUP_COMMANDS and len(cash) > 1:
            await message.reply( choice (cash [1:]))
        elif cash [0] in AVAILABLE_GROUP_COMMANDS:
            await message.reply( "Мне нужны варианты!" )

@dp.message_handler(MediaGroupFilter(), content_types=types.ContentType.PHOTO)
@media_group_handler
async def album_handler(messages: List[types.Message]):
    msg = choice(messages)
    await msg.reply_photo(msg.photo[-1].file_id)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def album_handler(message: types.Message):
    await message.reply_photo(message.photo[-1].file_id)

@dp.message_handler(content_types=types.ContentType.ANY)
async def master(message: types.Message):
    await message.reply("Извини, я пока не могу с таким работать. Попробуй /help")

if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except:
            time.sleep(5)