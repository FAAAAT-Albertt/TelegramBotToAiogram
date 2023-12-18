import aiogram
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ContentType, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from googletrans import Translator
import requests




but_langs = InlineKeyboardButton(text="🌐", callback_data="langs")
markup = InlineKeyboardMarkup(inline_keyboard=[[but_langs]])

but_sub = InlineKeyboardButton(text='Подписаться', url='t.me/Translator_School_Bot')
but_subber = InlineKeyboardButton(text='Подписался', callback_data='sub')
markup_sub = InlineKeyboardMarkup(inline_keyboard=[[but_sub],
                                                   [but_subber]])

BOT_TOKEN = '6460195162:AAG6P9ikpKTs_JFZ_C9LIs8W6mnig6krJZ8'

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

users = {}

langs = {
    "en": "Английский",
    "ru": "Русский",
    "de": "Немецкий",
    "ko": "Корейский",
    "uz": "Узбекский",
    "uk": "Украинский",
    "kk": "Казахский",
    "tg": "Таджитский",
    "tr": "Турецкий",
    "es": "Испанский",
    "fr": "Французский",
    "ja": "Японский",
    "ar": "Арабский",
    "zh-CN": "Китайский",
    "pl": "Польский",
    "ky": "Киргизский",
    "az": "Азербайджанский",
    "el": "Греческий",
    "pt": "Португальский",
    "fa": "Персидский",
    "it": "Итальянский",

    }

# приветствие
@dp.message(CommandStart())
async def command_start(message: Message):
    CHAT_ID = message.chat.id

    id_channel = "-1001932021320"

    is_admin = await admin_or_creator(CHAT_ID, id_channel)

    if is_admin:
        users[message.from_user.id] = {'text': ''}
        await message.answer("Отправь сюда свой текст, и бот в ту же секунду переведёт его на любой язык.\n\nПо умолчанию любой иностранный язык переводится на русский, а русский - на английский. Если хотите сменить язык, нажмите кнопку «🌐»")
    else:
        if message.from_user.id not in users:
            users[message.from_user.id] = {'text': '',
                                        'attemps': 10}

            await message.answer("Отправь сюда свой текст, и бот в ту же секунду переведёт его на любой язык.\n\nПо умолчанию любой иностранный язык переводится на русский, а русский - на английский. Если хотите сменить язык, нажмите кнопку «🌐»")
        else:
            if users[message.from_user.id]['attemps'] == 0:

                is_sub = await check_subscription(CHAT_ID, id_channel)
                if is_sub:
                    await message.answer("Отправь сюда свой текст, и бот в ту же секунду переведёт его на любой язык.\n\nПо умолчанию любой иностранный язык переводится на русский, а русский - на английский. Если хотите сменить язык, нажмите кнопку «🌐»")
                else:
                    await message.answer(text="У вас закончился бесплатный период.\n\nПожалуйста, оформите подписку", reply_markup=markup_sub)
            else:
                await message.answer("Отправь сюда свой текст, и бот в ту же секунду переведёт его на любой язык.\n\nПо умолчанию любой иностранный язык переводится на русский, а русский - на английский. Если хотите сменить язык, нажмите кнопку «🌐»")

# вывод перевода
@dp.message(F.text)
async def go_translate(message: Message):
    CHAT_ID = message.chat.id

    id_channel = "-1001932021320"


    is_admin = await admin_or_creator(CHAT_ID, id_channel)

    if is_admin:
        if message.from_user.id not in users:
                users[message.from_user.id] = {'text': message.text}
        else:
            users[message.from_user.id]['text'] = message.text

        txt = users[message.from_user.id]['text']
        src_approved = detected_text(txt)

        if src_approved == "ru":
            await message.answer(text=translate_text(text=txt, src=src_approved, dest='en'), reply_markup=markup)
        else:
            await message.answer(text=translate_text(text=txt, src=src_approved, dest='ru'), reply_markup=markup)

    else:
        is_sub = await check_subscription(CHAT_ID, id_channel)

        if is_sub:
            if message.from_user.id not in users:
                users[message.from_user.id] = {'text': message.text}
            else:
                users[message.from_user.id]['text'] = message.text

            txt = users[message.from_user.id]['text']
            src_approved = detected_text(txt)

            if src_approved == "ru":
                await message.answer(text=translate_text(text=txt, src=src_approved, dest='en'), reply_markup=markup)
            else:
                await message.answer(text=translate_text(text=txt, src=src_approved, dest='ru'), reply_markup=markup)

        else:
            if message.from_user.id not in users:
                users[message.from_user.id] = {'text': message.text,
                                            'attemps': 10}
            else:
                if users[message.from_user.id]['attemps'] == 0:
                    await message.answer(text="У вас закончился бесплатный период.\n\nПожалуйста, оформите подписку", reply_markup=markup_sub)

                else:
                    attemps = users[message.from_user.id]['attemps'] - 1
                    users[message.from_user.id] = {'text': message.text,
                                                'attemps': attemps}

                    txt = users[message.from_user.id]['text']
                    src_approved = detected_text(txt)

                    if src_approved == "ru":
                        await message.answer(text=translate_text(text=txt, src=src_approved, dest='en'), reply_markup=markup)
                    else:
                        await message.answer(text=translate_text(text=txt, src=src_approved, dest='ru'), reply_markup=markup)

# перевод текст
def translate_text(text, src, dest):
    try:
        translator = Translator()
        translation = translator.translate(text=text, src=src, dest=dest)
        return translation.text

    except Exception as ex:
        print(ex)

# определение языка
def detected_text(text):

    translator = Translator()
    detected_lang = translator.detect(text).lang
    return detected_lang

# генератор клавиатуры
def buitd_keydoard():

    builder = InlineKeyboardBuilder()
    buttons = []

    for data, button in langs.items():
        buttons.append(InlineKeyboardButton(text=button, callback_data=data))
    builder.row(*buttons, width=2)

    return builder.as_markup()


async def check_subscription(chat_id, channel_id):
    member = await bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
    if member.status == "member":
        return True

async def admin_or_creator(chat_id, channel_id):
    user = await bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
    if user.status == "administrator" or user.status == "creator":
        return True

# нужны проверки
# коллбэк обработчик
@dp.callback_query()
async def callback_but(callback: CallbackQuery):
    CHAT_ID = callback.message.chat.id
    id_channel = "-1001932021320"

    is_admin = await admin_or_creator(CHAT_ID, id_channel)
    is_sub = await check_subscription(CHAT_ID, id_channel)

    if is_admin or is_sub:
        if callback.data == "langs":
            await callback.message.edit_text(text=callback.message.text, reply_markup=buitd_keydoard())
            await callback.answer()

        else:
            for data, button in langs.items():
                if callback.data == data:
                    try:
                        await callback.message.edit_text(text=translate_text(text=callback.message.text, src=detected_text(callback.message.text), dest=data), reply_markup=buitd_keydoard())
                        await callback.answer()
                    except:
                        await callback.answer()
    else:
        if users[callback.message.chat.id]['attemps'] == 0:
            await callback.message.answer(text="У вас закончился бесплатный период.\n\nПожалуйста, оформите подписку", reply_markup=markup_sub)

        else:
            users[callback.message.chat.id]['attemps'] = users[callback.message.chat.id]['attemps'] - 1
            if callback.data == "langs":
                await callback.message.edit_text(text=callback.message.text, reply_markup=buitd_keydoard())
                await callback.answer()

            else:
                for data, button in langs.items():
                    if callback.data == data:
                        try:
                            await callback.message.edit_text(text=translate_text(text=callback.message.text, src=detected_text(callback.message.text), dest=data), reply_markup=buitd_keydoard())
                            await callback.answer()
                        except:
                            await callback.answer()


    if callback.data == 'sub':
        is_sub = await check_subscription(CHAT_ID, id_channel)
        if is_sub:
            await callback.message.answer("Отлично, теперь ты можешь пользоваться ботом без ограничений!")
        else:
            await callback.message.answer("Не вижу твоей подписки...", reply_markup=markup_sub)


if __name__ == '__main__':
    dp.run_polling(bot)