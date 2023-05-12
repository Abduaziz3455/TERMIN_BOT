from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def same_words(words):
    wordsMenu = InlineKeyboardMarkup(row_width=3)
    for key in words:
        wordsMenu.insert(InlineKeyboardButton(text=key, callback_data=key))
    return wordsMenu


def videos(text):
    videomenu = InlineKeyboardMarkup(row_width=1)
    videomenu.insert(InlineKeyboardButton(text="📺 Videoni ko'rish", callback_data=f"\\\\{text}"))
    return videomenu
