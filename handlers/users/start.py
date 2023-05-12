import re
import sqlite3
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from pytube import Search, YouTube
from data.config import CHANNELS, ADMINS
from handlers.users.find_word import checkWord
from handlers.users.read_word import word_atama
from keyboards.inline.right_word import same_words, videos
from keyboards.inline.subscription import check_button
from loader import dp, db, bot
from utils.misc import subscription
from aiogram.dispatcher.filters.state import StatesGroup, State


class Group(StatesGroup):
    subs = State()


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    await state.finish()
    name = message.from_user.full_name
    username = message.from_user.username
    id = message.from_user.id
    channels_format = str()
    for channel in CHANNELS:
        chat = await bot.get_chat(channel)
        invite_link = await chat.export_invite_link()
        # logging.info(invite_link)
        channels_format += f"👉 <a href='{invite_link}'>{chat.title}</a>\n"
    await message.answer(f"Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling: \n"
                         f"{channels_format}",
                         reply_markup=check_button,
                         disable_web_page_preview=True, parse_mode='HTML')


@dp.callback_query_handler(text="check_subs")
async def checker(call: types.CallbackQuery):
    await types.ChatActions.typing()
    await call.answer()
    name = call.from_user.full_name
    id = call.from_user.id
    username = call.from_user.username
    result = str()
    active = 0
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id,
                                          channel=channel)
        channel = await bot.get_chat(channel)
        invite_link = await channel.export_invite_link()
        if status:
            result += f"✅<a href='{invite_link}'>{channel.title}</a> kanaliga obuna bo'lgansiz!\n\n"
            active += 1
        else:
            result += (f"<b>{channel.title}</b> kanaliga obuna bo'lmagansiz. "
                       f"<a href='{invite_link}'>Obuna bo'ling</a>\n\n")
    await call.message.answer(result, disable_web_page_preview=True, parse_mode='HTML')
    if active == len(CHANNELS):
        await Group.subs.set()
        await call.message.delete()
        try:
            if not db.exist_user(id):
                db.add_user(id=call.message.from_user.id,
                            name=name, username=username)
                await call.message.answer(
                    f"Assalomu alaykum🖐! NDKTU ning 'Termin_bot' ga xush kelibsiz.\nBotdan foydalanish uchun biror "
                    f"fanga aloqador atama kiriting (masalan: xatolik, EYUK manbasi, fotoqarshilik va h.k")
                count = db.count_users()[0]
                msg = f"{name} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
                await bot.send_message(chat_id=ADMINS[0], text=msg)
            else:
                await call.message.answer(
                    f"Botdan foydalanish uchun biror fanga aloqador atama"
                    f" kiriting (masalan: xatolik, EYUK manbasi, fotoqarshilik va h.k)")
        except sqlite3.IntegrityError as err:
            await bot.send_message(chat_id=ADMINS[0], text=err)


@dp.message_handler(content_types='text', state=Group.subs)
async def checkImlo(message: types.Message):
    await types.ChatActions.typing()
    word = message.text.lower()
    result = checkWord(word)
    if result['available']:
        response = f"✅{word} 👉 {word_atama()[word]}"
        await message.answer(response, reply_markup=videos(word))
    else:
        response = f"❌{word} --> Bunday atama lug'atimizda mavjud emas!"
        if len(result['matches']) > 0:
            response += f"\n\nO'xshash so'zlar:\n"
        else:
            response += f"\nIltimos yangilanishlarni kuting."

        await message.answer(response, reply_markup=same_words(result['matches']))


@dp.callback_query_handler(lambda x: x.data, state=Group.subs)
async def ret_word(call: types.CallbackQuery):
    await types.ChatActions.typing()
    if call.data.split("\\\\") != 2:
        text = call.data
        response = f"✅{text} 👉 {word_atama()[text]}"
        # await call.message.delete()
        await call.message.answer(response, reply_markup=videos(text))
        await call.answer(cache_time=2)
    else:
        text = call.data.split("\\\\")[1]
        s = Search(query=text)
        for video in s.results[:5]:
            string_repr = str(video)

            match = re.search(r'videoId=([^>\s]+)', string_repr)
            if match:
                video_id = match.group(1)
                await call.message.answer(text=f'https://www.youtube.com/watch?v={video_id}')
        await call.answer()
