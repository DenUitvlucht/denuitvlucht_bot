
# CRONTAB FOR THIS FILE: 10 20 * * 4

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
    os.getcwd(), 'denuitvlucht_bot', 'output', 'order.xlsx')

next_tuesday = datetime.datetime.today() + datetime.timedelta(days=5)
next_tuesday_formatted = next_tuesday.strftime('_%d_%m_%y')

gmail = Gmail()

query_params = {
    "newer_than": (1, "day"),
}

messages = gmail.get_sent_messages(query=construct_query(query_params))


async def notify_bestuur(info):

    info.attachments[0].save(filepath=ORDER_OUTPUT)

    order = InputFile(ORDER_OUTPUT, filename=f"order{next_tuesday_formatted}.xlsx")

    await bot.send_document(chat_id=CHAT_ID, document=order, caption=f"❗ BESTELLING GEPLAATST ❗\n\nDag bestuursleden, ik heb daarnet jullie bestelling geplaatst. Hierboven vindt je het Excel bestand dat ik naar de brouwer heb gestuurd.\nJullie krijgen dit bericht elke donderdagavond.")

    os.remove(ORDER_OUTPUT)

if messages != []:

    for message in messages:

        if 'Bestelling JH Den Uitvlucht' in message.subject:

            bot = Bot(token=API_TOKEN)
            dp = Dispatcher(bot)

            asyncio.run(notify_bestuur(info=message))
