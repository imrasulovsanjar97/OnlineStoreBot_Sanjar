from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database

db = Database(DB_NAME)

next_prev_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='◀️', callback_data='prev'),
            InlineKeyboardButton(text='▶️', callback_data='next'),
        ]
    ]
)


def get_next_prev_keyboard(all_count, count=10, page=0):
    digits = []
    for i in range(count):
        digits.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=str(i)
            )
        )
    kb = [digits]
    if all_count > 10:
        kb.append([
            InlineKeyboardButton(text='◀️', callback_data='prev'),
            InlineKeyboardButton(text='▶️', callback_data='next'),
        ])
    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )
