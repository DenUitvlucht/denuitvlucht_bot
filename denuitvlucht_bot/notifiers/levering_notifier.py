
# CRONTAB FOR THIS FILE: 0 18 * * 2

import os
import asyncio
import datetime

from simplegmail import Gmail
from simplegmail.query import construct_query
from aiogram import Bot, Dispatcher
from aiogram.types.input_file import InputFile

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ORDER_OUTPUT = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'output', 'order.pdf')

today = datetime.datetime.today().strftime('_%d_%m_%y')

gmail = Gmail()

query_params = {
    "newer_than": (1, "day"),
}

messages = gmail.get_messages(query=construct_query(query_params))


async def notify_bestuur(info):

    info.attachments[0].save(filepath=ORDER_OUTPUT)

    order = InputFile(ORDER_OUTPUT, filename=f"delivery{today}.pdf")

    await bot.send_document(chat_id=CHAT_ID, document=order, caption=f"❗ LEVERING van {info.sender.split('<')[0]}❗\n\nDag bestuursleden, de Bockor-Boys zijn vandaag langsgeweest! Hierboven kan je de details van de levering vinden.\nJullie krijgen dit bericht elke dinsdagavond.")

    os.remove(ORDER_OUTPUT)

if messages != []:

    for message in messages:

        if 'Order Delivery' in message.subject:

            bot = Bot(token=API_TOKEN)
            dp = Dispatcher(bot)

            asyncio.run(notify_bestuur(info=message))
