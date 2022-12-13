
#!/usr/bin/python3

# CRONTAB FOR THIS FILE: 0 12 * * 1

import os
import asyncio
import datetime

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('BARBEZETTING')

week = f"{datetime.datetime.today().strftime('%d/%m')} - { (datetime.datetime.today() + datetime.timedelta(days=6)).strftime('%d/%m')}"


async def send_bar_poll(chat_id):

    await bot.send_poll(chat_id=chat_id, is_anonymous=False, allows_multiple_answers=True, question=f"🍻 Barbezeting Week {week}", options=["Woensdag", "Vrijdag", "Zaterdag"])


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

asyncio.run(send_bar_poll(chat_id=CHAT_ID))
