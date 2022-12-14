
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
from aiogram.types.input_file import InputFile
from aiogram.types.input_media import InputMediaPhoto
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from payments.payconiq import payconiq_auth, get_payment_profile_ids, get_totals_from_payment_profile_id
from payments.sumup import sumup_auth, get_access_token, get_refresh_token, get_sumup_transactions

from data.json_helper import read_from_json, write_to_json

from data.ffmpeg_helper import get_drankkot_snapshot

from bot.keyboards.general.general_keyboards import get_intro_keyboard
from bot.keyboards.general.general_keyboards import get_general_information_keyboard

from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_keyboard
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_category_keyboard
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_category_keyboard_edit
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_item_keyboard_edit
from bot.keyboards.brouwer.brouwer_keyboards import get_snapshot_keyboard

from bot.keyboards.shifts.shifts_keyboards import get_wc_keyboard

from bot.keyboards.rvb.rvb_keyboards import get_rvb_list_keyboard
from bot.keyboards.rvb.rvb_keyboards import get_rvb_list_keyboard_alt
from bot.keyboards.rvb.rvb_keyboards import get_wipe_rvb_list_confirmation_keyboard

from bot.keyboards.financial.financial_keyboards import get_financial_keyboard
from bot.keyboards.financial.financial_keyboards import get_payconiq_keyboard
from bot.keyboards.financial.financial_keyboards import get_payconiq_totals_keyboard
from bot.keyboards.financial.financial_keyboards import get_sumup_keyboard
from bot.keyboards.financial.financial_keyboards import get_sumup_totals_keyboard

from bot.keyboards.boodschappen.boodschappen_keyboards import get_boodschappen_keyboard
from bot.keyboards.boodschappen.boodschappen_keyboards import get_colruyt_card_keyboard
from bot.keyboards.boodschappen.boodschappen_keyboards import get_wipe_boodschappen_list_confirmation_keyboard
from bot.keyboards.boodschappen.boodschappen_keyboards import get_boodschappen_list_keyboard

# Define paths
AANBOD_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')
RVB_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'rvb_puntjes.json')
WC_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'wc_shift.json')
BOODSCHAPPEN_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'boodschappen.json')

# Load API TOKEN
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
BESTUUR_IDS = os.getenv('BESTUUR_IDS').split(',')
CHAT_ID = os.getenv('CHAT_ID').split(',')
CAM_USER = os.getenv('CAM_USER')
CAM_PASSWORD = os.getenv('CAM_PASSWORD')
CAM_IPV4 = os.getenv('CAM_IPV4')

PAYCONIQ_QR = os.path.join(os.getcwd(), 'denuitvlucht_bot', 'data', 'qr.jpg',)
COLRUYT_CARD = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'colruyt_card.jpg',)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Configure CallbackData
general_cd = CallbackData('vote', 'action')
brouwer_cd = CallbackData('vote', 'action')
item_cd = CallbackData('vote', 'action', 'name', 'amount', 'category')
rvb_cd = CallbackData('vote', 'action')
rvb_del_cd = CallbackData('vote', 'action', 'position')
wc_cd = CallbackData('vote', 'action')
financial_cd = CallbackData('vote', 'action')


''' 
------------------------------------------------------------------------------- GENERAL -------------------------------------------------------------------------------
'''

# SumUp Authorization


@dp.message_handler(commands=['start'])
async def sumup_authorization_handler(message: types.Message):

    args = message.get_args()
    if args != '' and str(message.from_id) in BESTUUR_IDS:

        get_refresh_token(code=args)

        await message.answer(text=f'Dag bestuurslid. *De SumUp authenticatie is voltooid!*\nJullie kunnen vanaf nu de transactie historiek opvragen via de bot.', parse_mode=ParseMode.MARKDOWN,)


# Start command handler
@dp.message_handler(commands=['denuitvlucht'])
async def cmd_start(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        await message.reply(f'Dag bestuurslid, wat kan ik voor je doen?', reply_markup=get_intro_keyboard())

    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


# General information callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['general_info']))
async def general_info_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        f'???? E-mail:\nbestuur@denuitvlucht.com\n\n???? Website:\ndenuitvlucht.com\n\n??????? Ondernemingsnummer:\n`0864.384.420`\n\n???? Rekeningnummer:\n`BE92 7380 1090 2923`\n\n',
        query.message.chat.id,
        query.message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_general_information_keyboard()
    )


# Close callback handler
@dp.callback_query_handler(general_cd.filter(action=['close']))
async def close_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.reply_to_message.message_id,
    )


# Main options callback handler
@dp.callback_query_handler(brouwer_cd.filter(action=['denuitvlucht']))
async def intro_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Dag bestuurslid, wat kan ik voor je doen?',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_intro_keyboard()
    )


''' 
------------------------------------------------------------------------------- BROUWER -------------------------------------------------------------------------------
'''

# Brouwer callback handler


@dp.callback_query_handler(brouwer_cd.filter(action=['brouwer_keyboard']))
async def brouwer_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    aanbod = read_from_json(path=AANBOD_JSON)

    overzicht = []
    bakken_count = 0
    for category in aanbod:

        for best in aanbod[category]:

            if int(best['amount']) > 0:

                type = 'vat(en)' if 'Liter' in best['name'] else 'toren(s)' if 'bekers' in best[
                    'name'] else 'fles(sen)' if 'CO2' in best['name'] else 'bak(ken)'
                overzicht.append(
                    f'*- {best["name"]} | {best["amount"]} {type}*\n')
                bakken_count += int(best['amount'])

    text = 'Dag brouwer,\n\n ?????? Momenteel staat er geen bestelling klaar.\n\n' if bakken_count == 0 else 'Dag brouwer,\n\n?????? Het aantal bakken van je bestelling ligt nog onder de 15!\n\n' if bakken_count < 15 else 'Dag brouwer,\n\ndit is je huidige bestelling:\n\n'
    # text = 'Dag brouwer, dit is je huidige bestelling:\n\n' if bakken_count > 0 else 'Dag brouwer, momenteel staat er geen bestelling klaar.'

    if 'photo' in query.message:

        await bot.delete_message(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
        )

        await query.message.reply_to_message.reply(
            f'{text}{"".join(overzicht)}\nDruk op onderstaande knop om de bestelling aan te passen of toe te voegen.',
            reply_markup=get_brouwer_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )

    else:

        await bot.edit_message_text(
            f'{text}{"".join(overzicht)}\nDruk op onderstaande knop om de bestelling aan te passen of toe te voegen.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_brouwer_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )


# Show drankkot callback handler
@dp.callback_query_handler(brouwer_cd.filter(action=['show_drankkot']))
async def show_drankkot_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    r = await query.message.reply_to_message.reply(
        'Even geduld...\nEr wordt een foto genomen van het drankkot.\nDit kan enkele seconden duren!'
    )

    snapshot_location = get_drankkot_snapshot(
        ipv4=CAM_IPV4,
        username=CAM_USER,
        password=CAM_PASSWORD
    )

    snapshot = InputFile(path_or_bytesio=snapshot_location)

    await query.message.reply_to_message.reply_photo(
        photo=snapshot,
        reply_markup=get_snapshot_keyboard()
    )

    await bot.delete_message(chat_id=r['chat']['id'], message_id=r['message_id'])

    os.remove(snapshot_location)


# Brouwer edit category callback handler
@dp.callback_query_handler(item_cd.filter(action=['brouwer_edit_current_order_category']))
async def brouwer_category_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    name = None if callback_data['name'] == '' else callback_data['name']
    amount = None if callback_data['amount'] == '' else callback_data['amount']

    await bot.edit_message_text(
        f'Klik op de categorie die je wil aanpassen!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_brouwer_category_keyboard(amount=amount, name=name)
    )


# Brouwer edit category callback handler
@dp.callback_query_handler(item_cd.filter(action=['edit_category']))
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(f"Categorie {callback_data['category']}",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_brouwer_category_keyboard_edit(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']))


# Brouwer edit item callback handler
@dp.callback_query_handler(item_cd.filter(action='edit_item'))  # Edit item
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    aanbod = read_from_json(path=AANBOD_JSON)

    item = [item for item in aanbod[callback_data['category']]
            if item['name'] == callback_data['name']][0]

    price_excl_btw = str(item['price_excl_btw']).replace('.', ',')
    price_incl_btw = str(item['price_incl_btw']).replace('.', ',')
    return_amount = str(item['return_amount']).replace('.', ',')
    unit_price = str(round(float(
        item['price_incl_btw']) + float(item['return_amount']), 2)).replace('.', ',')

    type = 'vat(en)' if 'Liter' in callback_data['name'] else 'toren(s)' if 'bekers' in callback_data[
        'name'] else 'fles(sen)' if 'CO2' in callback_data['name'] else 'bak(ken)'

    if type == 'vat(en)':

        selling_price_default = str(
            item['selling_price_default']).replace('.', ',')
        selling_price_members = str(
            item['selling_price_members']).replace('.', ',')
        prices = f'?????? *Informatie:*\nAankoopprijs excl. BTW: `???{price_excl_btw}`\nAankoopprijs incl. BTW: `???{price_incl_btw}`\nLeeggoed: `???{return_amount}`\nTotale aankoopprijs (incl. + leeggoed): `???{unit_price}`\nVerkoopprijs niet-leden: `???{selling_price_default}`\nVerkoopprijs leden: `???{selling_price_members}`\n\n'

    else:

        prices = f'?????? *Informatie:*\nAankoopprijs excl. BTW: `???{price_excl_btw}`\nAankoopprijs incl. BTW: `???{price_incl_btw}`\nLeeggoed: `???{return_amount}`\nTotale aankoopprijs (incl. + leeggoed): `???{unit_price}`\n\n'

    await bot.edit_message_text(f"{prices}Momenteel staan er *{callback_data['amount']}* {type} *{callback_data['name']}* in de bestelling",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_brouwer_item_keyboard_edit(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='plus'))  # Increment amount
async def vote_plus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    category = callback_data['category']
    amount = int(callback_data['amount'])
    amount += 1
    type = 'vat(en)' if 'Liter' in callback_data['name'] else 'toren(s)' if 'bekers' in callback_data[
        'name'] else 'fles(sen)' if 'CO2' in callback_data['name'] else 'bak(ken)'

    await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* {type} *{name}* in de bestelling.',
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_brouwer_item_keyboard_edit(amount, callback_data['name'], category), parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(item_cd.filter(action='minus'))  # Decrease amount
async def vote_minus_cb_handler(query: types.CallbackQuery, callback_data: dict):

    name = callback_data['name']
    amount = int(callback_data['amount'])
    category = callback_data['category']
    amount -= 1 if amount > 0 else 0

    type = 'vat(en)' if 'Liter' in callback_data['name'] else 'toren(s)' if 'bekers' in callback_data[
        'name'] else 'fles(sen)' if 'CO2' in callback_data['name'] else 'bak(ken)'

    if amount > -1:

        await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* {type} *{name}* in de bestelling.',
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=get_brouwer_item_keyboard_edit(amount, callback_data['name'], category=category), parse_mode=ParseMode.MARKDOWN)


''' 
------------------------------------------------------------------------------- FINANCIAL -----------------------------------------------------------------------------
'''

# Financial callback handler


@dp.callback_query_handler(rvb_cd.filter(action=['financial_keyboard']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Dag bestuurslid, dit zijn jouw opties:',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_financial_keyboard()
    )


# Payconiq callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_keyboard']))
async def payconiq_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    if 'photo' in query.message:

        await bot.delete_message(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
        )

        await query.message.reply_to_message.reply(
            text='Payconiq opties:',
            reply_markup=get_payconiq_keyboard()
        )

    else:
        await bot.edit_message_text(
            'Payconiq opties:',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_payconiq_keyboard()
        )


# Payconiq QR callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_qr']))
async def payconiq_qr_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    qr = InputFile(path_or_bytesio=PAYCONIQ_QR)

    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    await query.message.reply_to_message.reply_photo(
        photo=qr,
        reply_markup=get_payconiq_totals_keyboard()
    )


# Payconiq totals callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_totals']))
async def payconiq_totals_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    data = payconiq_auth()

    ids = get_payment_profile_ids(
        data['session'],
    )

    sticker_totals = get_totals_from_payment_profile_id(
        ids['session'],
        payment_profile_id=ids['payment_profile_id_sticker']
    )

    sticker_totals_text = '\n\n'.join(
        [f"{item['intervalType']}: `???{str(float(item['totals']['totalAmount']) / 100).replace('.', ',')}`\n-> {item['totals']['transactionCount']} transactie(s)" for item in sticker_totals])

    app_to_app_totals = get_totals_from_payment_profile_id(
        SESSION=ids['session'],
        payment_profile_id=ids['payment_profile_id_app_to_app']
    )

    app_to_app_totals_text = '\n\n'.join(
        [f"{item['intervalType']}: `???{str(float(item['totals']['totalAmount']) / 100).replace('.', ',')}`\n-> {item['totals']['transactionCount']} transactie(s)" for item in app_to_app_totals])

    await bot.edit_message_text(
        f'Dit is jullie Payconiq-overzicht:\n\n*Sticker:*\n\n{sticker_totals_text}\n\n*Online:*\n\n{app_to_app_totals_text}',
        query.message.chat.id,
        query.message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_payconiq_totals_keyboard()
    )


# SumUp callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['sumup_keyboard']))
async def sumup_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'SumUp opties:',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_sumup_keyboard()
    )


# SumUp Authorization callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['sumup_auth']))
async def sumup_auth_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    keyboard = InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('???? Login', url=sumup_auth())).add(
        types.InlineKeyboardButton('?????? Terug', callback_data=financial_cd.new(action='sumup_keyboard')))

    await bot.edit_message_text('*SumUp Authenticatie*\n\nJe zal doorgestuurd worden naar het OAuth2-portaal van Den Uitvlucht vzw', query.message.chat.id, query.message.message_id, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN,)


# SumUp totals calblack handler
@dp.callback_query_handler(rvb_cd.filter(action=['sumup_totals']))
async def sumup_totals_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    # Dates
    today = datetime.datetime.today()
    yesterday = (datetime.datetime.today() -
                 datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_of_week = (today - datetime.timedelta(
        days=today.weekday())).strftime('%Y-%m-%d')

    start_of_month = (today - datetime.timedelta(
        days=today.day-1)).strftime('%Y-%m-%d')

    access_token = get_access_token()

    transactions_since_yesterday = get_sumup_transactions(
        access_token=access_token,
        start_date=yesterday,
        end_date=today.strftime('%Y-%m-%d')
    )

    transactions_since_start_of_week = get_sumup_transactions(
        access_token=access_token,
        start_date=start_of_week,
        end_date=today.strftime('%Y-%m-%d')
    )

    transactions_since_start_of_month = get_sumup_transactions(
        access_token=access_token,
        start_date=start_of_month,
        end_date=today.strftime('%Y-%m-%d')
    )

    text = f"""*Totaal sinds gisteren:*\n`???{transactions_since_yesterday["revenue"]}`\n-> {transactions_since_yesterday["transaction_count"]} transacties\n\n
*Totaal sinds begin van de week:*\n`???{transactions_since_start_of_week["revenue"]}`\n-> {transactions_since_start_of_week["transaction_count"]} transacties\n\n
*Totaal sinds begin van de maand:*\n`???{transactions_since_start_of_month["revenue"]}`\n-> {transactions_since_start_of_month["transaction_count"]} transacties\n\n
    """

    await bot.edit_message_text(text, query.message.chat.id, query.message.message_id, parse_mode=ParseMode.MARKDOWN, reply_markup=get_sumup_totals_keyboard())


''' 
------------------------------------------------------------------------------- RVB -----------------------------------------------------------------------------------
'''

# Add Form


class Form(StatesGroup):

    puntje = State()  # Will be represented in storage as 'Form:puntje'

# Add form handler


@dp.message_handler(state=Form.puntje)
async def process_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:

        data['puntje'] = message.text

    await state.finish()

    await message.reply(f'??? *Puntje: "{data["puntje"]}" is toegevoegd!*', parse_mode=ParseMode.MARKDOWN)

    rvb_list = read_from_json(path=RVB_JSON)
    rvb_list['puntjes'].append({
        'subject': data["puntje"],
        'date': str(datetime.datetime.today().strftime("%d/%m/%Y")),
        'who': f'{message.from_user.first_name}'
    })

    write_to_json(path=RVB_JSON, data=rvb_list)


# Add command handler


@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        args = message.text.split(' ')

        if len(args) == 1:

            await Form.puntje.set()
            await message.reply(f'???? *Dag bestuurslid, wat wil je toevoegen aan de lijst?*', parse_mode=ParseMode.MARKDOWN)

        elif len(args) > 1:

            puntje = ' '.join(args[1:])
            await message.reply(f'??? *Puntje: "{puntje}" is toegevoegd!*', parse_mode=ParseMode.MARKDOWN)

            rvb_list = read_from_json(path=RVB_JSON)
            rvb_list['puntjes'].append({
                'subject': puntje,
                'date': str(datetime.datetime.today().strftime("%d/%m/%Y")),
                'who': f'{message.from_user.first_name}'
            })

            write_to_json(path=RVB_JSON, data=rvb_list)
    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


# Wipe rvb list callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['wipe_rvb_list']))
async def wipe_rvb_list_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

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


# Wipe rvn list confirmation callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['wipe_rvb_list_confirmation']))
async def wipe_rvb_list_confirmation_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Ben je zeker dat je de RVB-puntjes wil wissen?',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_wipe_rvb_list_confirmation_keyboard()
    )


# RVB list callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['rvb_list']))
async def rvb_list_callback(query: types.CallbackQuery):

    await query.answer()

    rvb_list = read_from_json(path=RVB_JSON)

    overzicht = []
    for item in rvb_list['puntjes']:

        who = item['who'] if 'who' in item else 'onbekend'
        overzicht.append(
            f'*- {item["subject"]}* | Toegevoegd op *{item["date"]}* door *{who}* \n\n')

    if len(overzicht) > 0:

        await bot.edit_message_text(
            f'Dit zijn de RVB-puntjes van deze week:\n\n{"".join(overzicht)}',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_rvb_list_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )

    else:

        await bot.edit_message_text(
            f'Er zijn nog geen RVB-puntjes toegevoegd.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_rvb_list_keyboard_alt()
        )


# RVB list edit callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['rvb_list_edit']))
async def rvb_list_edit_callback(query: types.CallbackQuery):

    await query.answer()

    rvb_list = read_from_json(path=RVB_JSON)

    keyboard = InlineKeyboardMarkup()
    count = 0
    for item in rvb_list['puntjes']:

        index = rvb_list['puntjes'].index(item)

        keyboard.row(types.InlineKeyboardButton(
            text=f"{item['subject']}", callback_data=rvb_del_cd.new(action=f'rvb_delete_item', position=index)))
        count += 1

    if count > 0:

        keyboard.row(types.InlineKeyboardButton(
            '?????? Terug', callback_data=rvb_cd.new(action='rvb_list')))

        await bot.edit_message_text(
            f'Klik op een punje om het uit de lijst te verwijderen.\n\n',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

    else:

        keyboard = InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(
            '?????? Terug', callback_data=rvb_cd.new(action='rvb_list')))

        await bot.edit_message_text(
            f'Er zijn geen RVB-puntjes meer om te verwijderen.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=keyboard
        )


# RVB list edit callback handler
@dp.callback_query_handler(rvb_del_cd.filter(action=['rvb_delete_item']))
async def rvb_list_callback(query: types.CallbackQuery):

    await query.answer()

    item_position = int(query.data.split('rvb_delete_item:')[1])

    rvb_list = read_from_json(path=RVB_JSON)

    item_subject = rvb_list['puntjes'][item_position]['subject']

    rvb_list['puntjes'].pop(item_position)

    write_to_json(path=RVB_JSON, data=rvb_list)

    keyboard = InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(
        '?????? Terug', callback_data=rvb_cd.new(action='rvb_list_edit')))

    await bot.edit_message_text(
        f'Puntje *{item_subject}* is verwijderd!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


# List command handler
@dp.message_handler(commands=['list'])
async def rvb_list_command(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        rvb_list = read_from_json(path=RVB_JSON)

        overzicht = []
        for item in rvb_list['puntjes']:

            who = item['who'] if 'who' in item else 'onbekend'
            overzicht.append(
                f'*- {item["subject"]}* | Toegevoegd op *{item["date"]}* door *{who}* \n\n')

        if len(overzicht) > 0:

            keyboard = InlineKeyboardMarkup().row(types.InlineKeyboardButton('??????? Individuele items verwijderen', callback_data=rvb_cd.new(action='rvb_list_edit'))
                                                  ).row(types.InlineKeyboardButton('??????? Volledige lijst wissen', callback_data=rvb_cd.new(action='wipe_rvb_list_confirmation'))).row(types.InlineKeyboardButton(
                                                      '??? Sluiten', callback_data=general_cd.new(action='close')))

            await message.reply(
                f'Dit zijn de RVB-puntjes van deze week:\n\n{"".join(overzicht)}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )

        else:

            await message.reply(
                f'Er zijn nog geen RVB-puntjes toegevoegd.',
            )

    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


''' 
------------------------------------------------------------------------------- BOODSCHAPPEN --------------------------------------------------------------------------
'''

# Boodschappen callback handler


@dp.callback_query_handler(rvb_cd.filter(action=['boodschappen_keyboard']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    if 'photo' in query.message:

        await bot.delete_message(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
        )

        await query.message.reply_to_message.reply(
            text='Boodschappen opties',
            reply_markup=get_boodschappen_keyboard()
        )

    else:

        await bot.edit_message_text(
            'Boodschappen opties:',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_boodschappen_keyboard()
        )


# Colruyt card callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['colruyt_card']))
async def colruyt_card_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    card = InputFile(path_or_bytesio=COLRUYT_CARD)

    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    await query.message.reply_to_message.reply_photo(
        photo=card,
        reply_markup=get_colruyt_card_keyboard()
    )


# Boodschap command handler
@dp.message_handler(commands=['boodschap'])
async def cmd_boodschap(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        args = message.text.split(' ')

        if len(args) == 1:

            await message.reply(f'?????? *Vergeet je boodschap niet te vermelden!*', parse_mode=ParseMode.MARKDOWN)

        elif len(args) > 1:

            boodschap = ' '.join(args[1:])
            await message.reply(f'???? *Boodschap: "{boodschap}" is toegevoegd!*', parse_mode=ParseMode.MARKDOWN)

            boodschappen_list = read_from_json(path=BOODSCHAPPEN_JSON)
            boodschappen_list['boodschappen'].append({
                'item': boodschap,
            })

            write_to_json(path=BOODSCHAPPEN_JSON, data=boodschappen_list)
    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


# Wipe boodschappen list callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['wipe_boodschappen_list']))
async def wipe_boodschappen_list_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    # CLEAR JSON

    boodschappen_list = read_from_json(path=BOODSCHAPPEN_JSON)

    boodschappen_list['boodschappen'] = []

    write_to_json(path=BOODSCHAPPEN_JSON, data=boodschappen_list)

    await bot.edit_message_text(
        'De boodschappen zijn gewist!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_colruyt_card_keyboard()
    )


# Wipe boodschappen list confirmation callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['wipe_boodschappen_list_confirmation']))
async def wipe_rvb_list_confirmation_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Ben je zeker dat je de boodschappenlijst wil wissen?',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_wipe_boodschappen_list_confirmation_keyboard()
    )


# Boodschappen list callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['boodschappen_list']))
async def rvb_list_callback(query: types.CallbackQuery):

    await query.answer()

    boodschappen_list = read_from_json(path=BOODSCHAPPEN_JSON)

    overzicht = []
    for item in boodschappen_list['boodschappen']:

        who = item['who'] if 'who' in item else 'onbekend'
        overzicht.append(
            f'*- {item["item"]}*\n\n')

    if len(overzicht) > 0:

        await bot.edit_message_text(
            f'Dit is het huidige boodschappenlijstje:\n\n{"".join(overzicht)}',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_boodschappen_list_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )

    else:

        await bot.edit_message_text(
            f'Er staat nog niks op het boodschappenlijstje.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_colruyt_card_keyboard()
        )


# Boodschappen list edit callback handler
@dp.callback_query_handler(rvb_cd.filter(action=['boodschappen_list_edit']))
async def boodschappen_list_edit_callback(query: types.CallbackQuery):

    await query.answer()

    boodschappen_list = read_from_json(path=BOODSCHAPPEN_JSON)

    keyboard = InlineKeyboardMarkup()
    count = 0
    for item in boodschappen_list['boodschappen']:

        index = boodschappen_list['boodschappen'].index(item)

        keyboard.row(types.InlineKeyboardButton(
            text=f"{item['item']}", callback_data=rvb_del_cd.new(action=f'boodschappen_delete_item', position=index)))
        count += 1

    if count > 0:

        keyboard.row(types.InlineKeyboardButton(
            '?????? Terug', callback_data=rvb_cd.new(action='boodschappen_list')))

        await bot.edit_message_text(
            f'Klik op het item om het uit de lijst te verwijderen.\n\n',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

    else:

        keyboard = InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(
            '?????? Terug', callback_data=rvb_cd.new(action='boodschappen_list')))

        await bot.edit_message_text(
            f'Er zijn geen items meer om te verwijderen.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=keyboard
        )


# Boodschappen list delete item callback handler
@dp.callback_query_handler(rvb_del_cd.filter(action=['boodschappen_delete_item']))
async def rvb_list_callback(query: types.CallbackQuery):

    await query.answer()

    item_position = int(query.data.split('boodschappen_delete_item:')[1])

    boodschappen_list = read_from_json(path=BOODSCHAPPEN_JSON)

    item_subject = boodschappen_list['boodschappen'][item_position]['item']

    boodschappen_list['boodschappen'].pop(item_position)

    write_to_json(path=BOODSCHAPPEN_JSON, data=boodschappen_list)

    keyboard = InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(
        '?????? Terug', callback_data=rvb_cd.new(action='boodschappen_list_edit')))

    await bot.edit_message_text(
        f'Item *{item_subject}* is verwijderd!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


''' 
------------------------------------------------------------------------------- SHIFTS -------------------------------------------------------------------------------- 
'''


# WC shift callback handler
@dp.callback_query_handler(wc_cd.filter(action=['wc_shift']))
async def wc_shift_callback(query: types.CallbackQuery):

    await query.answer()

    shifts = read_from_json(path=WC_JSON)

    # search for person with has_to_clean == true
    for shift in shifts['shifts']:

        if shift['has_to_clean'] == True:

            has_to_clean = shift['name']

    await bot.edit_message_text(
        f'???? *{has_to_clean}* moet deze week volgende taakjes doen:\n\n- WC kuisen\n- Was naar wasserette\n- Glas naar glasbol',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_wc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query_handler(wc_cd.filter(action='next_wc_shift'))
async def next_wc_shift_handler(query: types.CallbackQuery, callback_data: dict):

    shifts = read_from_json(path=WC_JSON)

    for index, shift in enumerate(shifts['shifts']):

        if shift['has_to_clean'] == True:

            shift['has_to_clean'] = False

            if shifts['shifts'].index(shift) < len(shifts['shifts']) - 1:

                shifts['shifts'][index+1]['has_to_clean'] = True
                has_to_clean = shifts['shifts'][index+1]['name']
            else:
                shifts['shifts'][0]['has_to_clean'] = True
                has_to_clean = shifts['shifts'][0]['name']

            break

    write_to_json(path=WC_JSON, data=shifts)

    await bot.edit_message_text(f'???? *{has_to_clean}* moet deze week de WC kuisen. Veel kuisplezier!',
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_wc_keyboard(),
                                parse_mode=ParseMode.MARKDOWN
                                )


# handle the cases when this exception raises
@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
