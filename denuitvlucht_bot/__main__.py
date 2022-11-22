
#!/usr/bin/python3

import logging
import os
import typing

from dotenv import load_dotenv

from datetime import datetime as dt

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, ParseMode
from aiogram.utils.exceptions import MessageNotModified


from data.json_helper import read_from_aanbod_json, write_to_aanbod_json

# Define paths
AANBOD_JSON = os.path.join(os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')

# Load API TOKEN
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
BESTUUR_IDS = os.getenv('BESTUUR_IDS').split(',')
CHAT_ID = os.getenv('CHAT_ID').split(',')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Configure CallbackData
brouwer_cd = CallbackData('vote', 'action')
item_cd = CallbackData('vote', 'action', 'name', 'amount', 'category')

# Keyboards
def get_intro_keyboard():  # Main options for bestuur
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton(
            'Brouwer', callback_data=brouwer_cd.new(action='brouwer_keyboard'))
    )


def get_brouwer_keyboard():  # Brouwer keyboard with option(s)
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('Huidige bestelling', callback_data=item_cd.new(
            action='brouwer_edit_current_order_category', name='', amount='', category='')),
    ).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(action='denuitvlucht')))


def get_brouwer_category_keyboard(name, amount):  # Category keyboard

    keyboard = InlineKeyboardMarkup()

    aanbod = read_from_aanbod_json(path=AANBOD_JSON)

    for category in aanbod:

        keyboard.row(types.InlineKeyboardButton(
            text=category, callback_data=item_cd.new(action=f'edit_category', name='', amount='', category=category)))

    keyboard.row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(
        action='brouwer_keyboard')))
    return keyboard


# Keyboard with all items and their amounts
def get_brouwer_edit_category_keyboard(name, amount, category):

    aanbod = read_from_aanbod_json(path=AANBOD_JSON)

    # Write new data if needed

    if name != '' and amount != '':

        for best in aanbod[category]:

            if name in best['name']:

                best['amount'] = amount
        
        write_to_aanbod_json(path=AANBOD_JSON, data=aanbod)

        aanbod = read_from_aanbod_json(path=AANBOD_JSON)

    keyboard = InlineKeyboardMarkup()

    for optie in aanbod[category]:

        keyboard.row(types.InlineKeyboardButton(
            text=f"{optie['name']} | {optie['amount']} bakken", callback_data=item_cd.new(action=f'edit_item', name=optie['name'], amount=optie['amount'], category=category)))

    keyboard.row(types.InlineKeyboardButton('⬅️ Terug', callback_data=item_cd.new(
        action='brouwer_edit_current_order_category', name='', amount='', category=category)))
    return keyboard


def get_edit_keyboard(amount, name, category):  # Keyboard to change amounts
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('⬇️ Verlaag', callback_data=item_cd.new(
            action='minus', amount=amount, name=name, category=category)),

        types.InlineKeyboardButton('⬆️ Verhoog', callback_data=item_cd.new(
            action='plus', amount=amount, name=name, category=category))

    ).row(types.InlineKeyboardButton('⬅️ Terug en opslaan', callback_data=item_cd.new(
        action=f'edit_category', name=name, amount=amount, category=category)))


# Handlers
@dp.message_handler(commands=['denuitvlucht'])  # Start handler
async def cmd_start(message: types.Message):
    
    if str(message.from_id) in BESTUUR_IDS and str(message.chat.id) in CHAT_ID:

        await message.reply(f'Dag bestuurslid, wat kan ik voor je doen?', reply_markup=get_intro_keyboard())
    
    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden in de bestuursgroep, door een toegelaten bestuurslid.')


# Main options for bestuur
@dp.callback_query_handler(brouwer_cd.filter(action=['denuitvlucht']))
async def intro_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Dag bestuurslid, wat kan ik voor je doen?',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_intro_keyboard()
    )


# Brouwer option(s)
@dp.callback_query_handler(brouwer_cd.filter(action=['brouwer_keyboard']))
async def brouwer_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):


    await query.answer()

    await bot.edit_message_text(
        'Dag brouwer, dit zijn jouw opties:\n',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_brouwer_keyboard()
    )


# Categories
@dp.callback_query_handler(item_cd.filter(action=['brouwer_edit_current_order_category']))
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    name = None if callback_data['name'] == '' else callback_data['name']
    amount = None if callback_data['amount'] == '' else callback_data['amount']

    await bot.edit_message_text(
        f'Dit is jullie huidige bestelling.\nKlik op de categorie die je wil aanpassen!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_brouwer_category_keyboard(amount=amount, name=name)
    )


# All items and their amounts
@dp.callback_query_handler(item_cd.filter(action=['edit_category']))
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(f"Categorie {callback_data['category']}",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_brouwer_edit_category_keyboard(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']))


@dp.callback_query_handler(item_cd.filter(action='edit_item'))  # Edit item
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(f"Momenteel staan er *{callback_data['amount']}* bakken *{callback_data['name']}* in de bestelling",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_edit_keyboard(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='plus'))  # Increment amount
async def vote_plus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    category = callback_data['category']
    amount = int(callback_data['amount'])
    amount += 1

    await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* bakken *{name}* in de bestelling.',
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_edit_keyboard(amount, callback_data['name'], category), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='minus'))  # Decrease amount
async def vote_minus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    amount = int(callback_data['amount'])
    category = callback_data['category']
    amount -= 1 if amount > 0 else 0

    if amount > -1:

        await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* bakken *{name}* in de bestelling.',
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=get_edit_keyboard(amount, callback_data['name'], category=category), parse_mode=ParseMode.MARKDOWN)


# handle the cases when this exception raises
@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
