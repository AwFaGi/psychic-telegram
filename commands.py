from aiogram import types
from random import randrange


async def help_func(message: types.Message):
    s = "Для выбора текстовых значений, напиши их по одному в строке.\n" \
        "Для выбора фотографий, отправь их в одном сообщении\n" + \
        "\n".join([f"<i>/{i}:</i> {bot_commands[i][1]}" for i in bot_commands.keys()])
    await message.answer(s, parse_mode="HTML")


async def dice_func(message: types.Message):
    await message.reply_dice()


async def range_func(message: types.Message):
    try:
        arguments = list(map(int, message.get_args().split()))
        if len(arguments) == 0:
            await message.reply(str(randrange(1, 101)))
        else:
            await message.reply(str(randrange(*arguments)))
    except Exception:
        s = "<b>Произошла ошибка!<b>\n" \
            "Правильное использование:\n" \
            "<code>/range конец\n" \
            "/range начало конец\n" \
            "/range начало конец шаг\n" \
            "</code>"
        await message.reply(s, parse_mode="HTML")


bot_commands = {
    "help": (help_func, "Пишет данную справку."),
    "dice": (dice_func, "Бросает кубик."),
    "range": (range_func,
              "Принимает до 3 целых чисел. "
              "Возвращает целое число из указанного промежутка. "
              "По умолчанию:<i><code>/range 1 100</code></i>"
              )
}
