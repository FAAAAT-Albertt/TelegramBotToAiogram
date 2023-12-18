import asyncio
import openai
import aiohttp
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes
import logging


DESC_TEXT = """
1) Умножение -> *
2) Деление -> /
3) Степень -> ^
4) Косинус -> cos x
5) Синус -> sin x
6) Тангенс -> tg x
7) Котангенс -> ctg x
8) Натуральный логарифм -> ln x
9) Десятичный логарифм -> lg x
10) Логарифм -> log x
11) Производная -> '
12) Экспонента -> Е
13) Число Пи -> тт
14) Корень -> sqrt(x)
"""


ib1 = InlineKeyboardButton("Подписаться", url="https://t.me/school_aid")
ib2 = InlineKeyboardButton("Подписался", callback_data="sub")
ikb = InlineKeyboardMarkup(row_width=2).add(ib1).add(ib2)

reply_but = KeyboardButton(text="Аннотации")
reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(reply_but)

TOKEN = "6430017299:AAG9NZj0A9o7caoOTtV_rnOuOhZGLRkoudQ"
openai.api_key = "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"


messages = [
    {"role": "system", "content": "Ты математический калькулятор, который решает примеры и объясняет этапы решения, постарайся выдавать ответ в одном формате."},
    {"role": "user", "content": "Меня зовут Пользователь, я пришел присылать тебе математические примеры, чтобы ты их решал"},
    {"role": "assistant", "content": "Привет! Готов решать примеры?"}
]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
log = logging.basicConfig(level=logging.INFO)


def update(messages: list[dict], role: str, content: str):
    messages.append({'role': role, "content": content})

    return messages

def generate_response(messages: list[dict]):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    return response['choices'][0]['message']['content']

dp.message_handler(commands='start')
async def start_bot(message: types.Message):
    await message.answer('Жду твой запрос...')
    await message.delete()



async def check_subscription(chat_id, channel_id):
    member = await bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
    return member.is_chat_member()

async def admin_or_creator(chat_id, channel_id):
    user = await bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
    if user.status == "administrator" or user.status == "creator":
        return True


@dp.message_handler(commands='start')
async def start_bot(message: types.Message):

    CHAT_ID = message.chat.id
    id_channel = "-1001932021320"
    is_director = await admin_or_creator(CHAT_ID, id_channel)
    is_sub = await check_subscription(CHAT_ID, id_channel)

    if is_sub or is_director:
        await message.answer('Жду твой запрос...', reply_markup=reply_markup)
        await message.delete()

    else:
        await message.answer(text="Для начала подпишись на канал!", reply_markup=ikb)

@dp.message_handler(text="Аннотации")
async def look_desc(message: types.Message):

    CHAT_ID = message.chat.id
    id_channel = "-1001932021320"
    is_director = await admin_or_creator(CHAT_ID, id_channel)
    is_sub = await check_subscription(CHAT_ID, id_channel)

    if is_sub or is_director:
        await message.answer(text=DESC_TEXT)
    else:
        await message.answer(text="Для начала подпишись на канал!", reply_markup=ikb)


@dp.message_handler(content_types=ContentTypes.TEXT)
async def prompt(message: types.Message):
    global messages

    CHAT_ID = message.chat.id
    id_channel = "-1001932021320"
    is_director = await admin_or_creator(CHAT_ID, id_channel)
    is_sub = await check_subscription(CHAT_ID, id_channel)

    if is_sub or is_director:

        sent_mess = await message.answer("⏳Подготовка ответа…")
        messages = update(messages, "user", message.text)
        await message.reply(generate_response(messages))
        messages = update(messages, "assistant", generate_response(messages))
        await bot.delete_message(chat_id=message.chat.id, message_id=sent_mess.message_id)

    else:
        await message.answer(text="Для начала подпишись на канал!", reply_markup=ikb)

@dp.callback_query_handler()
async def check_sub(callback: types.CallbackQuery):

    CHAT_ID = callback.message.chat.id
    id_channel = "-1001932021320"
    is_director = await admin_or_creator(CHAT_ID, id_channel)
    is_sub = await check_subscription(CHAT_ID, id_channel)

    if callback.data == "sub":

        if is_sub or is_director:
            await callback.message.answer('Жду твой запрос...')

        else:
            await callback.message.answer("Не вижу твоей подписки...", reply_markup=ikb)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
