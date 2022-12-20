
from aiogram import types
from aiogram.utils.callback_data import CallbackData


boodschappen_cd = CallbackData('vote', 'action')

def get_boodschappen_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Colruyt-kaart', callback_data=boodschappen_cd.new(action='colruyt_card'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=boodschappen_cd.new(action='denuitvlucht')))

def get_colruyt_card_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=boodschappen_cd.new(action='boodschappen_keyboard')))

