
#!/usr/bin/python3

# CRONTAB FOR THIS FILE: 10 20 * * 4

import os
import asyncio
import datetime

from aiogram import Bot, Dispatcher
from aiogram.types.input_file import InputFile
from aiogram.types import ParseMode

from dotenv import load_dotenv

from gmail_helper import check_credentials, get_attachment_data, get_message_attachment

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ORDER_OUTPUT = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'output', 'order.xlsx')

next_tuesday = datetime.datetime.today() + datetime.timedelta(days=5)
next_tuesday_formatted = next_tuesday.strftime('_%d_%m_%y')
yesterday = (datetime.datetime.today() -
             datetime.timedelta(days=1)).strftime('%y/%m/%d')


async def notify_bestuur(data):

    with open(ORDER_OUTPUT, 'wb') as f:
        f.write(data)
        f.close()

    order = InputFile(
        ORDER_OUTPUT, filename=f"order{next_tuesday_formatted}.xlsx")

    await bot.send_document(chat_id=CHAT_ID, document=order, caption=f"❗ *BESTELLING GEPLAATST* ❗\n\nDag bestuursleden, ik heb daarnet jullie bestelling geplaatst.\n\nHierboven vindt je het Excel bestand dat ik naar de brouwer heb gestuurd.\n\nJullie krijgen dit bericht elke donderdag.", parse_mode=ParseMode.MARKDOWN)

    os.remove(ORDER_OUTPUT)

check_credentials()

order_attachment = get_message_attachment(location=['SENT'], queries=[
    'subject:Bestelling JH Den Uitvlucht', 'to:bestelling@omer.be', f'after:{yesterday}'])

if order_attachment['attachment_id'] is not None:

    data = get_attachment_data(
        message_id=order_attachment['message_id'], attachment_id=order_attachment['attachment_id'])

    if data is not None:

        bot = Bot(token=API_TOKEN)
        dp = Dispatcher(bot)

        asyncio.run(notify_bestuur(data=data))
