
#!/usr/bin/python3

import os
import datetime

from openpyxl import load_workbook

from json_helper import read_from_aanbod_json, write_to_aanbod_json

from simplegmail import Gmail

from dotenv import load_dotenv

load_dotenv()

TO = os.getenv('TO')
FROM = os.getenv('FROM')

# FILE LOCATIONS

BESTELLING_JSON_LOCATION = os.path.join(os.getcwd(), 'denuitvlucht_bot', 'data', 'aanbod.json')
BESTELLING_EXCEL_LOCATION = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'data', 'den_uitvlucht.xlsx')

next_tuesday = datetime.datetime.today() + datetime.timedelta(days=5)
next_tuesday_formatted = next_tuesday.strftime('_%d_%m_%y')

BESTELLING_EXCEL_OUTPUT = os.path.join(
    os.getcwd(), 'denuitvlucht_bot', 'output', f'den_uitvlucht{next_tuesday_formatted}.xlsx')

# READ BESTELLING FOR JSON

bestelling_json = read_from_aanbod_json(
    path=BESTELLING_JSON_LOCATION
)

# LOAD EMPTY EXCEL FILE

workbook = load_workbook(
    filename=BESTELLING_EXCEL_LOCATION
)

sheet = workbook.active

# FILL EXCEL FILE WITH AMOUNTS AND SAVE

valid = False
for category in bestelling_json:

    for item in bestelling_json[category]:

        if item['amount'] != '0':

            valid = True
        
        if valid:

            sheet[item['excel_location']
                ] = item['amount'] if item['amount'] != '0' else ''
        else:

            exit(1)

workbook.save(filename=BESTELLING_EXCEL_OUTPUT)

# INITIALIZE GMAIL

gmail = Gmail()

# DEFINE PARAMS

params = {
  "to": TO,
  "sender": FROM,
  "cc": [],
  "bcc": [],
  "subject": "Bestelling JH Den Uitvlucht",
  "msg_html": "Beste<br /><br />In bijlage vindt u de bestelling voor volgende week.<br /><br />Met vriendelijke groeten<br /><br />Team Den Uitvlucht",
  "msg_plain": "Nieuwe bestelling JH Den Uitvlucht",
  "attachments": [BESTELLING_EXCEL_OUTPUT],
  "signature": True
}

# SEND E-MAIL

message = gmail.send_message(**params)

# CLEAR JSON

for category in bestelling_json:

    for item in bestelling_json[category]:

        item['amount'] = '0'

write_to_aanbod_json(
    path=BESTELLING_JSON_LOCATION,
    data=bestelling_json
)

# DELETE EXCEL

os.remove(BESTELLING_EXCEL_OUTPUT)

