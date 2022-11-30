
#!/usr/bin/python3

import logging
import os
import typing
import datetime

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, ParseMode
from aiogram.utils.exceptions import MessageNotModified


from data.json_helper import read_from_json, write_to_json

# Define paths
AANBOD_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')
RVB_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'rvb_puntjes.json')

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
rvb_cd = CallbackData('vote', 'action')

# Keyboards


def get_intro_keyboard():  # Main options for bestuur
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton(
            '🍺 Brouwer', callback_data=brouwer_cd.new(action='brouwer_keyboard'))).row(types.InlineKeyboardButton(
                '✔️ RVB-puntjes', callback_data=rvb_cd.new(action='rvb_list'))
    )


def get_brouwer_keyboard():  # Brouwer keyboard with option(s)
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('Bestelling aanpassen/toevoegen', callback_data=item_cd.new(
            action='brouwer_edit_current_order_category', name='', amount='', category='')),
    ).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(action='denuitvlucht')))


def get_rvb_list_keyboard():  # Brouwer keyboard with option(s)
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('🗑️ Wis lijst', callback_data=rvb_cd.new(action='wipe_rvb_list'))).row(types.InlineKeyboardButton('⬅️ Terug', callback_data=rvb_cd.new(action='denuitvlucht')))

def get_rvb_list_keyboard_alt():  # Brouwer keyboard with option(s)
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('⬅️ Terug', callback_data=rvb_cd.new(action='denuitvlucht')))


def get_brouwer_category_keyboard(name, amount):  # Category keyboard

    keyboard = InlineKeyboardMarkup()

    aanbod = read_from_json(path=AANBOD_JSON)

    for category in aanbod:

        keyboard.row(types.InlineKeyboardButton(
            text=category, callback_data=item_cd.new(action=f'edit_category', name='', amount='', category=category)))

    keyboard.row(types.InlineKeyboardButton('⬅️ Terug', callback_data=brouwer_cd.new(
        action='brouwer_keyboard')))
    return keyboard


# Keyboard with all items and their amounts
def get_brouwer_edit_category_keyboard(name, amount, category):

    aanbod = read_from_json(path=AANBOD_JSON)

    # Write new data if needed

    if name != '' and amount != '':

        for best in aanbod[category]:

            if name in best['name']:

                best['amount'] = amount

        write_to_json(path=AANBOD_JSON, data=aanbod)

        aanbod = read_from_json(path=AANBOD_JSON)

    keyboard = InlineKeyboardMarkup()

    for optie in aanbod[category]:

        type = 'bak(ken)' if 'Liter' not in optie['name'] else 'vat(en)'

        keyboard.row(types.InlineKeyboardButton(
            text=f"{optie['name']} | {optie['price']} | {optie['amount']} {type}", callback_data=item_cd.new(action=f'edit_item', name=optie['name'], amount=optie['amount'], category=category)))

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

# Add handler
@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS and str(message.chat.id) in CHAT_ID:

        args = message.text.split(' ')

        if len(args) == 1:

            await message.reply(f'Vergeet je puntje niet te vermelden!.')

        elif len(args) > 1:

            puntje = ' '.join(args[1:])
            await message.reply(f'Puntje: "{puntje}" is toegevoegd!')

        rvb_list = read_from_json(path=RVB_JSON)
        rvb_list['puntjes'].append({
            'subject': puntje,
            'date': str(datetime.datetime.today().strftime("%d/%m/%Y"))
        })

        write_to_json(path=RVB_JSON, data=rvb_list)
    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden in de bestuursgroep, door een toegelaten bestuurslid.')
    
# Wipe handler
@dp.callback_query_handler(rvb_cd.filter(action=['wipe_rvb_list']))
async def intro_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    # CLEAR JSON

    rvb_list = read_from_json(path=RVB_JSON)

    rvb_list['puntjes'] = []

    write_to_json(path=RVB_JSON, data=rvb_list)

    await bot.edit_message_text(
        'De RVB-puntjes zijn gewist!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_rvb_list_keyboard_alt()
    )


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

    aanbod = read_from_json(path=AANBOD_JSON)

    overzicht = []
    count = 0
    for category in aanbod:

        for best in aanbod[category]:

            if int(best['amount']) > 0:

                type = 'bak(ken)' if 'Liter' not in best['name'] else 'vat(en)'
                overzicht.append(
                    f'- {best["name"]} | {best["amount"]} {type}\n')
                count += 1

    text = 'Dag brouwer, dit is je huidige bestelling:\n\n' if count > 0 else 'Dag brouwer, momenteel staat er geen bestelling klaar.'

    await bot.edit_message_text(
        f'{text}{"".join(overzicht)}\nDruk op onderstaande knop om de bestelling aan te passen of toe te voegen.',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_brouwer_keyboard()
    )

# RVB LIST
@dp.callback_query_handler(rvb_cd.filter(action=['rvb_list']))
async def rvb_list_callback(query: types.CallbackQuery):

    await query.answer()

    rvb_list = read_from_json(path=RVB_JSON)

    overzicht = []
    for item in rvb_list['puntjes']:

        overzicht.append(
            f'- {item["subject"]} | Toegevoegd op {item["date"]} \n')

    if len(overzicht) > 0:

        await bot.edit_message_text(
            f'Dit zijn de RVB-puntjes van deze week:\n\n{"".join(overzicht)}',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_rvb_list_keyboard()
        )
    
    else:

        await bot.edit_message_text(
            f'Er zijn nog geen RVB-puntjes toegevoegd.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_rvb_list_keyboard_alt()
        )


# Categories
@dp.callback_query_handler(item_cd.filter(action=['brouwer_edit_current_order_category']))
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    name = None if callback_data['name'] == '' else callback_data['name']
    amount = None if callback_data['amount'] == '' else callback_data['amount']

    await bot.edit_message_text(
        f'Klik op de categorie die je wil aanpassen!',
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

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'

    await bot.edit_message_text(f"Momenteel staan er *{callback_data['amount']}* {type} *{callback_data['name']}* in de bestelling",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_edit_keyboard(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='plus'))  # Increment amount
async def vote_plus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    category = callback_data['category']
    amount = int(callback_data['amount'])
    amount += 1

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'

    await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* {type} *{name}* in de bestelling.',
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_edit_keyboard(amount, callback_data['name'], category), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='minus'))  # Decrease amount
async def vote_minus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    amount = int(callback_data['amount'])
    category = callback_data['category']
    amount -= 1 if amount > 0 else 0

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'

    if amount > -1:

        await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* {type} *{name}* in de bestelling.',
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=get_edit_keyboard(amount, callback_data['name'], category=category), parse_mode=ParseMode.MARKDOWN)


# handle the cases when this exception raises
@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
