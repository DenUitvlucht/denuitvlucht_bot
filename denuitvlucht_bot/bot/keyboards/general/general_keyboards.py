

from aiogram import types
from aiogram.utils.callback_data import CallbackData

general_cd = CallbackData('vote', 'action')
brouwer_cd = CallbackData('vote', 'action')
rvb_cd = CallbackData('vote', 'action')
wc_cd = CallbackData('vote', 'action')
financial_cd = CallbackData('vote', 'action')


def get_intro_keyboard():  # Main options for bestuur
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton(
            '🍺 Brouwer', callback_data=brouwer_cd.new(action='brouwer_keyboard'))).row(types.InlineKeyboardButton(
                '💵 Financieel', callback_data=financial_cd.new(action='financial_keyboard'))).row(types.InlineKeyboardButton(
                    '📖 RVB-puntjes', callback_data=rvb_cd.new(action='rvb_list'))).row(types.InlineKeyboardButton(
                        '🚽 WC-shift', callback_data=wc_cd.new(action='wc_shift'))).row(types.InlineKeyboardButton(
                        'ℹ️ Algemene Info', callback_data=general_cd.new(action='general_info'))
    )

