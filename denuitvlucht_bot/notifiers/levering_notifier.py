
#!/usr/bin/python3

# CRONTAB FOR THIS FILE: 0 18 * * 2


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
    os.getcwd(), 'denuitvlucht_bot', 'output', 'order.pdf')

today = datetime.datetime.today().strftime('_%d_%m_%y')
yesterday = (datetime.datetime.today() -
             datetime.timedelta(days=1)).strftime('%y/%m/%d')


async def notify_bestuur(data):

    with open(ORDER_OUTPUT, 'wb') as f:
        f.write(data)
        f.close()

    order = InputFile(ORDER_OUTPUT, filename=f"delivery{today}.pdf")

    await bot.send_document(chat_id=CHAT_ID, document=order, caption=f"❗ *LEVERING van OMER* ❗\n\nDag bestuursleden, de Bockor-Boys zijn vandaag langsgeweest!\n\nHierboven kan je de details van de levering vinden.\n\nJullie krijgen dit bericht elke dinsdag.", parse_mode=ParseMode.MARKDOWN)

    os.remove(ORDER_OUTPUT)

check_credentials()

delivery_attachment = get_message_attachment(location=['INBOX'], queries=[
    'subject:Order Delivery ', 'from:camion', f'after:{yesterday}'])

if delivery_attachment['attachment_id'] is not None:

    data = get_attachment_data(
        message_id=delivery_attachment['message_id'], attachment_id=delivery_attachment['attachment_id'])

    if data is not None:

        bot = Bot(token=API_TOKEN)
        dp = Dispatcher(bot)

        asyncio.run(notify_bestuur(data=data))
