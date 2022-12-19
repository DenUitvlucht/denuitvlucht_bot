
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

from payments.payconiq import auth, get_payment_profile_ids, get_totals_from_payment_profile_id
from payments.sumup import auth, get_access_token, get_refresh_token, get_sumup_transactions

from data.json_helper import read_from_json, write_to_json

from bot.keyboards.general.general_keyboards import get_intro_keyboard

from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_keyboard
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_category_keyboard
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_category_keyboard_edit
from bot.keyboards.brouwer.brouwer_keyboards import get_brouwer_item_keyboard_edit

from bot.keyboards.shifts.shifts_keyboards import get_wc_keyboard

from bot.keyboards.rvb.rvb_keyboards import get_rvb_list_keyboard
from bot.keyboards.rvb.rvb_keyboards import get_rvb_list_keyboard_alt
from bot.keyboards.rvb.rvb_keyboards import get_wipe_rvb_list_confirmation_keyboard

from bot.keyboards.financial.financial_keyboards import get_financial_keyboard
from bot.keyboards.financial.financial_keyboards import get_payconiq_keyboard
from bot.keyboards.financial.financial_keyboards import get_payconiq_totals_keyboard

from bot.keyboards.boodschappen.boodschappen_keyboards import get_boodschappen_keyboard


# Define paths
AANBOD_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')
RVB_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'rvb_puntjes.json')
WC_JSON = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'wc_shift.json')

# Load API TOKEN
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
BESTUUR_IDS = os.getenv('BESTUUR_IDS').split(',')
CHAT_ID = os.getenv('CHAT_ID').split(',')

PAYCONIQ_QR = os.path.join(os.getcwd(), 'denuitvlucht_bot', 'data', 'qr.jpg',)
COLRUYT_CARD = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'colruyt_card.jpg',)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Configure CallbackData
general_cd = CallbackData('vote', 'action')
brouwer_cd = CallbackData('vote', 'action')
item_cd = CallbackData('vote', 'action', 'name', 'amount', 'category')
rvb_cd = CallbackData('vote', 'action')
rvb_del_cd = CallbackData('vote', 'action', 'position')
wc_cd = CallbackData('vote', 'action')


# Handlers

@dp.message_handler(commands=['start'])
async def handler(message: types.Message):

    args = message.get_args()
    if args != '' and str(message.from_id) in BESTUUR_IDS:

        get_refresh_token(code=args)
    
        await message.answer(text=f'Dag bestuurslid. *De SumUp authenticatie is voltooid!*\nJullie kunnen vanaf nu de transactie historiek opvragen via de bot.', parse_mode=ParseMode.MARKDOWN,)


@dp.message_handler(commands=['sumupauth'])
async def handler(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        keyboard = InlineKeyboardMarkup().add(
            types.InlineKeyboardButton('🔑 Login', url=auth()))

        await message.reply(text='*SumUp Authenticatie*\n\nJe zal doorgestuurd worden naar het OAuth2-portaal van Den Uitvlucht vzw', reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN,)
    else:
        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


@dp.message_handler(commands=['sumup'])
async def handler(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

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

        text = f'''*Totaal sinds gisteren:*\n€{transactions_since_yesterday["revenue"]}\n-> {transactions_since_yesterday["transaction_count"]} transacties\n\n
*Totaal sinds begin van de week:*\n€{transactions_since_start_of_week["revenue"]}\n-> {transactions_since_start_of_week["transaction_count"]} transacties\n\n
*Totaal sinds begin van de maand:*\n€{transactions_since_start_of_month["revenue"]}\n-> {transactions_since_start_of_month["transaction_count"]} transacties\n\n
        '''

        await message.reply(text=text, parse_mode=ParseMode.MARKDOWN,)
    else:
        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


@dp.message_handler(commands=['denuitvlucht'])  # Start handler
async def cmd_start(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        await message.reply(f'Dag bestuurslid, wat kan ik voor je doen?', reply_markup=get_intro_keyboard())

    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')


@dp.callback_query_handler(rvb_cd.filter(action=['general_info']))
async def general_info_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        f'📧 E-mail:\nbestuur@denuitvlucht.com\n\n🌐 Website:\ndenuitvlucht.com\n\n🗄️ Ondernemingsnummer:\n`0864.384.420`\n\n💳 Rekeningnummer:\n`BE92 7380 1090 2923`',
        query.message.chat.id,
        query.message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_rvb_list_keyboard_alt()
    )


@dp.callback_query_handler(rvb_cd.filter(action=['financial_keyboard']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Dag bestuurslid, dit zijn jouw opties:',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_financial_keyboard()
    )


@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_keyboard']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Payconiq opties:',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_payconiq_keyboard()
    )


@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_qr']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    qr = InputFile(path_or_bytesio=PAYCONIQ_QR)

    await bot.send_photo(
        photo=qr,
        chat_id=query.message.chat.id
    )


@dp.callback_query_handler(rvb_cd.filter(action=['payconiq_totals']))
async def payconiq_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    data = auth()

    ids = get_payment_profile_ids(
        data['session'],
    )

    sticker_totals = get_totals_from_payment_profile_id(
        ids['session'],
        payment_profile_id=ids['payment_profile_id_sticker']
    )

    sticker_totals_text = '\n\n'.join(
        [f"{item['intervalType']}: *€{str(float(item['totals']['totalAmount']) / 100).replace('.', ',')}*\n-> {item['totals']['transactionCount']} transactie(s)" for item in sticker_totals])

    app_to_app_totals = get_totals_from_payment_profile_id(
        SESSION=ids['session'],
        payment_profile_id=ids['payment_profile_id_app_to_app']
    )

    app_to_app_totals_text = '\n\n'.join(
        [f"{item['intervalType']}: *€{str(float(item['totals']['totalAmount']) / 100).replace('.', ',')}*\n-> {item['totals']['transactionCount']} transactie(s)" for item in app_to_app_totals])

    await bot.edit_message_text(
        f'Dit is jullie Payconiq-overzicht:\n\nSticker:\n\n{sticker_totals_text}\n\nOnline:\n\n{app_to_app_totals_text}',
        query.message.chat.id,
        query.message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_payconiq_totals_keyboard()
    )


@dp.callback_query_handler(rvb_cd.filter(action=['boodschappen_keyboard']))
async def financial_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Boodschappen opties:',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_boodschappen_keyboard()
    )


@dp.callback_query_handler(rvb_cd.filter(action=['colruyt_card']))
async def colruyt_card_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    card = InputFile(path_or_bytesio=COLRUYT_CARD)

    await bot.send_photo(
        photo=card,
        chat_id=query.message.chat.id
    )


@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):

    if str(message.from_id) in BESTUUR_IDS:

        args = message.text.split(' ')

        if len(args) == 1:

            await message.reply(f'⚠️ *Vergeet je puntje niet te vermelden!*', parse_mode=ParseMode.MARKDOWN)

        elif len(args) > 1:

            puntje = ' '.join(args[1:])
            await message.reply(f'✅ *Puntje: "{puntje}" is toegevoegd!*', parse_mode=ParseMode.MARKDOWN)

            rvb_list = read_from_json(path=RVB_JSON)
            rvb_list['puntjes'].append({
                'subject': puntje,
                'date': str(datetime.datetime.today().strftime("%d/%m/%Y")),
                'who': f'{message.from_user.first_name}'
            })

            write_to_json(path=RVB_JSON, data=rvb_list)
    else:

        await message.reply(f'Sorry deze bot kan enkel gebruikt worden door een toegelaten bestuurslid.')

# Wipe handler


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

# Wipe handler


@dp.callback_query_handler(rvb_cd.filter(action=['wipe_rvb_list_confirmation']))
async def intro_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(
        'Ben je zeker dat je de RVB-puntjes wil wissen?',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_wipe_rvb_list_confirmation_keyboard()
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
    bakken_count = 0
    for category in aanbod:

        for best in aanbod[category]:

            if int(best['amount']) > 0:

                type = 'bak(ken)' if 'Liter' not in best['name'] else 'vat(en)'
                overzicht.append(
                    f'*- {best["name"]} | {best["amount"]} {type}*\n')
                bakken_count += int(best['amount'])

    text = 'Dag brouwer,\n\n ⚠️ Momenteel staat er geen bestelling klaar.\n\n' if bakken_count == 0 else 'Dag brouwer,\n\n⚠️ Het aantal bakken van je bestelling ligt nog onder de 15! ⚠️\n\n' if bakken_count < 15 else 'Dag brouwer,\n\ndit is je huidige bestelling:\n\n'
    #text = 'Dag brouwer, dit is je huidige bestelling:\n\n' if bakken_count > 0 else 'Dag brouwer, momenteel staat er geen bestelling klaar.'

    await bot.edit_message_text(
        f'{text}{"".join(overzicht)}\nDruk op onderstaande knop om de bestelling aan te passen of toe te voegen.',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_brouwer_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# RVB LIST


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
            '⬅️ Terug', callback_data=rvb_cd.new(action='rvb_list')))

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
            '⬅️ Terug', callback_data=rvb_cd.new(action='rvb_list')))

        await bot.edit_message_text(
            f'Er zijn geen RVB-puntjes meer op te verwijderen.',
            query.message.chat.id,
            query.message.message_id,
            reply_markup=keyboard
        )


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
        '⬅️ Terug', callback_data=rvb_cd.new(action='rvb_list_edit')))

    await bot.edit_message_text(
        f'Puntje *{item_subject}* is verwijderd!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


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

            keyboard = InlineKeyboardMarkup().row(types.InlineKeyboardButton('🖊️ Individuele items verwijderen', callback_data=rvb_cd.new(action='rvb_list_edit'))
                                                  ).row(types.InlineKeyboardButton('🗑️ Volledige lijst wissen', callback_data=rvb_cd.new(action='wipe_rvb_list_confirmation')))

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

# WC SHIFT


@dp.callback_query_handler(wc_cd.filter(action=['wc_shift']))
async def wc_shift_callback(query: types.CallbackQuery):

    await query.answer()

    shifts = read_from_json(path=WC_JSON)

    # search for person with has_to_clean == true
    for shift in shifts['shifts']:

        if shift['has_to_clean'] == True:

            has_to_clean = shift['name']

    await bot.edit_message_text(
        f'🚽 *{has_to_clean}* moet deze week de WC kuisen. Veel kuisplezier!',
        query.message.chat.id,
        query.message.message_id,
        reply_markup=get_wc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# WC SHIFT NEXT


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

    await bot.edit_message_text(f'🚽 *{has_to_clean}* moet deze week de WC kuisen. Veel kuisplezier!',
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_wc_keyboard(),
                                parse_mode=ParseMode.MARKDOWN
                                )

# Categories


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


# All items and their amounts
@dp.callback_query_handler(item_cd.filter(action=['edit_category']))
async def brouwer_edit_bestelling_callback(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):

    await query.answer()

    await bot.edit_message_text(f"Categorie {callback_data['category']}",
                                query.message.chat.id,
                                query.message.message_id,
                                reply_markup=get_brouwer_category_keyboard_edit(amount=callback_data['amount'], name=callback_data['name'], category=callback_data['category']))


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

    prices = f'ℹ️ *Informatie:*\nAankoopprijs excl. BTW: `€{price_excl_btw}`\nAankoopprijs incl. BTW: `€{price_incl_btw}`\nLeeggoed: `€{return_amount}`\nTotale aankoopprijs (incl. + leeggoed): `€{unit_price}`\n\n'

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'
    #prices = f'Prijs excl. BTW: `{callback_data["price_excl_btw"]}`\nPrijs incl. BTW `{callback_data["price_incl_btw"]}`'

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

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'

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

    type = 'bak(ken)' if 'Liter' not in callback_data['name'] else 'vat(en)'

    if amount > -1:

        await bot.edit_message_text(f'Aantal aangepast! Er staan nu *{amount}* {type} *{name}* in de bestelling.',
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=get_brouwer_item_keyboard_edit(amount, callback_data['name'], category=category), parse_mode=ParseMode.MARKDOWN)


# handle the cases when this exception raises
@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
