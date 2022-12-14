

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
            'đē Brouwer', callback_data=brouwer_cd.new(action='brouwer_keyboard'))).row(types.InlineKeyboardButton(
                'đĩ Financieel', callback_data=financial_cd.new(action='financial_keyboard'))).row(types.InlineKeyboardButton(
                    'đ RVB-puntjes', callback_data=rvb_cd.new(action='rvb_list'))).row(types.InlineKeyboardButton(
                        'đ Boodschappen', callback_data=rvb_cd.new(action='boodschappen_keyboard'))).row(types.InlineKeyboardButton(
                            'đŊ Taakjes', callback_data=wc_cd.new(action='wc_shift'))).row(types.InlineKeyboardButton(
                                'âšī¸ Algemene Info', callback_data=general_cd.new(action='general_info'))).row(types.InlineKeyboardButton(
                                    'â Sluiten', callback_data=general_cd.new(action='close'))
    )

def get_general_information_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Uitleendienst Jeugd', url='https://www.waregem.be/formulieren/uitleendienst-jeugd')
    ).row(types.InlineKeyboardButton('Activiteitenfiche aanvragen', url='https://www.waregem.be/formulieren/activiteitenfiche')
    ).row(types.InlineKeyboardButton('Website Formaat', url='https://formaat.be/')
    ).row(types.InlineKeyboardButton('Dekasound catalogus', url='https://www.dekasound.be/catalog')
    ).row(types.InlineKeyboardButton('RoVaRi catalogus', url='https://www.rovari.be/verhuur-1')
    ).row(types.InlineKeyboardButton('Wachtwoordenkluis', url='https://vault.bitwarden.com/#/login')
    ).row(types.InlineKeyboardButton('âŦī¸ Terug', callback_data=rvb_cd.new(action='denuitvlucht'))
    )
    