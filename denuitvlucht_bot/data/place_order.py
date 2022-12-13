
#!/usr/bin/python3

import os
import datetime

from openpyxl import load_workbook

from json_helper import read_from_json, write_to_json

from simplegmail import Gmail

from dotenv import load_dotenv

from gmail_helper import check_credentials, gmail_send_message_with_attachment

load_dotenv()

TO = os.getenv('TO')
FROM = os.getenv('FROM')

# FILE LOCATIONS

BESTELLING_JSON_LOCATION = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')
BESTELLING_EXCEL_LOCATION = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'den_uitvlucht.xlsx')

next_tuesday = datetime.datetime.today() + datetime.timedelta(days=5)
next_tuesday_formatted = next_tuesday.strftime('_%d_%m_%y')

BESTELLING_EXCEL_OUTPUT = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'output', f'den_uitvlucht{next_tuesday_formatted}.xlsx')

# READ BESTELLING FOR JSON

bestelling_json = read_from_json(
    path=BESTELLING_JSON_LOCATION
)

# LOAD EMPTY EXCEL FILE

workbook = load_workbook(
    filename=BESTELLING_EXCEL_LOCATION
)

sheet = workbook.active

# FILL EXCEL FILE WITH AMOUNTS AND SAVE

bakken_count = 0
for category in bestelling_json:

    for item in bestelling_json[category]:

        if item['amount'] != '0':

            bakken_count += int(item['amount'])

            sheet[item['excel_location']
                  ] = item['amount']

if bakken_count < 15:

    exit(1)

workbook.save(filename=BESTELLING_EXCEL_OUTPUT)

# INITIALIZE GMAIL

check_credentials()

# SEND E-MAIL

gmail_send_message_with_attachment(
    attachment=BESTELLING_EXCEL_OUTPUT,
    attachment_name=f'den_uitvlucht{next_tuesday_formatted}.xlsx',
    message='Beste\n\nIn bijlage vindt u de bestelling voor volgende week.\n\nMet vriendelijke groeten\n\nTeam Den Uitvlucht',
    receiver=TO,
    sender=FROM,
    subject='Bestelling JH Den Uitvlucht',
)

# CLEAR JSON

for category in bestelling_json:

    for item in bestelling_json[category]:

        item['amount'] = '0'

write_to_json(
    path=BESTELLING_JSON_LOCATION,
    data=bestelling_json
)

# DELETE EXCEL

os.remove(BESTELLING_EXCEL_OUTPUT)
