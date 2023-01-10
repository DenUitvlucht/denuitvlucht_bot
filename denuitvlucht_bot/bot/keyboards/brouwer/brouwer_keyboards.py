
import os

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from data.json_helper import read_from_json, write_to_json

AANBOD_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')

brouwer_cd = CallbackData('vote', 'action')
rvb_cd = CallbackData('vote', 'action')
item_cd = CallbackData('vote', 'action', 'name', 'amount', 'category')
rvb_del_cd = CallbackData('vote', 'action', 'position')
wc_cd = CallbackData('vote', 'action')
financial_cd = CallbackData('vote', 'action')


def get_brouwer_keyboard():  # Brouwer keyboard with option(s)
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton(
            '🖊️ Bestelling aanpassen/toevoegen', callback_data=item_cd.new(
                action='brouwer_edit_current_order_category', name='', amount='', category='')),
    ).row(types.InlineKeyboardButton(
        '📷 Drankkot bekijken', callback_data=brouwer_cd.new(action='show_drankkot'))).row(types.InlineKeyboardButton(
        '⬅️ Terug', callback_data=brouwer_cd.new(action='denuitvlucht')))


def get_brouwer_category_keyboard(name, amount):  # Category keyboard

    keyboard = types.InlineKeyboardMarkup()

    aanbod = read_from_json(path=AANBOD_JSON)

    for category in aanbod:

        keyboard.row(types.InlineKeyboardButton(
            text=category, callback_data=item_cd.new(action=f'edit_category', name='', amount='', category=category)))

    keyboard.row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(
        action='brouwer_keyboard')))
    return keyboard

# Keyboard with all items and their amounts


def get_brouwer_category_keyboard_edit(name, amount, category):

    aanbod = read_from_json(path=AANBOD_JSON)

    # Write new data if needed

    if name != '' and amount != '':

        for best in aanbod[category]:

            if name in best['name']:

                best['amount'] = amount

        write_to_json(path=AANBOD_JSON, data=aanbod)

        aanbod = read_from_json(path=AANBOD_JSON)

    keyboard = types.InlineKeyboardMarkup()

    for optie in aanbod[category]:

        type = 'vat(en)' if 'Liter' in optie['name'] else 'toren(s)' if 'bekers' in optie['name'] else 'bak(ken)'

        keyboard.row(types.InlineKeyboardButton(
            text=f"{optie['name']} | €{str(round(float(optie['price_incl_btw']) + float(optie['return_amount']), 2)).replace('.',',')} | {optie['amount']} {type}", callback_data=item_cd.new(action=f'edit_item', name=optie['name'], amount=optie['amount'], category=category)))

    keyboard.row(types.InlineKeyboardButton('⬅️ Terug', callback_data=item_cd.new(
        action='brouwer_edit_current_order_category', name='', amount='', category=category)))
    return keyboard


# Keyboard to change amounts
def get_brouwer_item_keyboard_edit(amount, name, category):
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('⬇️ Verlaag', callback_data=item_cd.new(
            action='minus', amount=amount, name=name, category=category)),

        types.InlineKeyboardButton('⬆️ Verhoog', callback_data=item_cd.new(
            action='plus', amount=amount, name=name, category=category))

    ).row(types.InlineKeyboardButton('⬅️ Terug en opslaan', callback_data=item_cd.new(
        action=f'edit_category', name=name, amount=amount, category=category)))

def get_snapshot_keyboard(): 
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(action='brouwer_keyboard')))
