

from aiogram import types
from aiogram.utils.callback_data import CallbackData

wc_cd = CallbackData('vote', 'action')


def get_wc_keyboard():  # WC keyboard with option(s)
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('⏩ Volgende shift', callback_data=wc_cd.new(
            action='next_wc_shift')),
    ).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=wc_cd.new(action='denuitvlucht')))
