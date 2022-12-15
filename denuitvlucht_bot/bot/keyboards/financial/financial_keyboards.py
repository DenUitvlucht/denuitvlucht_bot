
from aiogram import types
from aiogram.utils.callback_data import CallbackData


financial_cd = CallbackData('vote', 'action')


def get_financial_keyboard():  # Financial keyboard with option(s)
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Payconiq-overzicht', callback_data=financial_cd.new(action='payconiq'))).row(types.InlineKeyboardButton('Payconiq QR', callback_data=financial_cd.new(action='payconiq_qr'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='denuitvlucht')))


def get_payconiq_keyboard():  # Payconiq keyboard
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='financial_keyboard')))
