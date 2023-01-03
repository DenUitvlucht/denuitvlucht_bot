
from aiogram import types
from aiogram.utils.callback_data import CallbackData


boodschappen_cd = CallbackData('vote', 'action')

def get_boodschappen_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Colruyt-kaart', callback_data=boodschappen_cd.new(action='colruyt_card'))).row(types.InlineKeyboardButton('Lijstje', callback_data=boodschappen_cd.new(action='boodschappen_list'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=boodschappen_cd.new(action='denuitvlucht')))

def get_colruyt_card_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=boodschappen_cd.new(action='boodschappen_keyboard')))

def get_boodschappen_list_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('🖊️ Individuele items verwijderen', callback_data=boodschappen_cd.new(action='boodschappen_list_edit'))).row(types.InlineKeyboardButton('🗑️ Volledige lijst wissen', callback_data=boodschappen_cd.new(action='wipe_boodschappen_list_confirmation'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=boodschappen_cd.new(action='boodschappen_keyboard')))

def get_wipe_boodschappen_list_confirmation_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('✅ JA', callback_data=boodschappen_cd.new(action='wipe_boodschappen_list'))).row(types.InlineKeyboardButton('❌ NEE', callback_data=boodschappen_cd.new(action='boodschappen_list')))