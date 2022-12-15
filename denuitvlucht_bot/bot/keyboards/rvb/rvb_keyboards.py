

from aiogram import types
from aiogram.utils.callback_data import CallbackData


rvb_cd = CallbackData('vote', 'action')


def get_rvb_list_keyboard():  # RVB List keyboard with option(s)
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('🖊️ Individuele items verwijderen', callback_data=rvb_cd.new(action='rvb_list_edit'))).row(types.InlineKeyboardButton('🗑️ Volledige lijst wissen', callback_data=rvb_cd.new(action='wipe_rvb_list_confirmation'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=rvb_cd.new(action='denuitvlucht')))


def get_rvb_list_keyboard_alt():  # Alt RVB List keyboard with option(s)
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=rvb_cd.new(action='denuitvlucht')))


def get_wipe_rvb_list_confirmation_keyboard():  # RVB List confirmation keyboard
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('✅ JA', callback_data=rvb_cd.new(action='wipe_rvb_list'))).row(types.InlineKeyboardButton('❌ NEE', callback_data=rvb_cd.new(action='rvb_list')))
