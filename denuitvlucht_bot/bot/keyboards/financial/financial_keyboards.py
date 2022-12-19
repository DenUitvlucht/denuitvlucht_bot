
from aiogram import types
from aiogram.utils.callback_data import CallbackData


financial_cd = CallbackData('vote', 'action')


def get_financial_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Payconiq', callback_data=financial_cd.new(action='payconiq_keyboard'))).row(types.InlineKeyboardButton('SumUp', callback_data=financial_cd.new(action='sumup_keyboard'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='denuitvlucht')))

def get_payconiq_keyboard():
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('📔 Payconiq-overzicht', callback_data=financial_cd.new(action='payconiq_totals'))).row(types.InlineKeyboardButton('📷 Payconiq QR', callback_data=financial_cd.new(action='payconiq_qr'))).row(types.InlineKeyboardButton('🌐 Payconiq Betaalpagina', url='https://payconiq.com/merchant/1/621f67961664270008a56b96')).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='financial_keyboard')))

def get_payconiq_totals_keyboard():
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='payconiq_keyboard')))

def get_sumup_keyboard():
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('📔 SumUp-overzicht', callback_data=financial_cd.new(action='sumup_totals'))).row(types.InlineKeyboardButton('🔑 SumUp-auth', callback_data=financial_cd.new(action='sumup_auth'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='financial_keyboard')))

def get_sumup_totals_keyboard():
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=financial_cd.new(action='sumup_keyboard')))