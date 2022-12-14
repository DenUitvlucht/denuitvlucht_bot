
import requests
import os
import datetime

from dotenv import load_dotenv

load_dotenv()

PAYCONIQ_EMAIL = os.getenv('PAYCONIQ_EMAIL')
PAYCONIQ_PASSWORD = os.getenv('PAYCONIQ_PASSWORD')

PAYCONIQ_AUTH_URL = 'https://portal.payconiq.com/merchant-portal/api/merchants/authentications/tokens'
PAYCONIQ_PAYMENT_PROFILES_URL = 'https://portal.payconiq.com/merchant-portal/api/merchant/payment-profiles/search'
PAYCONIQ_TOTALS_URL = 'https://portal.payconiq.com/merchant-portal/api/transactions/totals'

TOTAL_SUMMARIES = ['Vandaag', 'Deze week', 'Deze maand', 'Dit jaar']
def auth():

    SESSION = requests.Session()

    SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
    })

    r = SESSION.post(
        url=PAYCONIQ_AUTH_URL,
        json={
            'email': PAYCONIQ_EMAIL,
            'password': PAYCONIQ_PASSWORD
        }
    )

    r.raise_for_status()

    return {
        'session': SESSION,
        'merchant_id': r.json()['merchant_id']
    }


def get_payment_profile_ids(SESSION: requests.Session):

    SESSION.headers.update(
        {
            'x-xsrf-token': SESSION.cookies.get_dict()['XSRF-TOKEN'],
            'Content-Type': 'application/json;charset=utf-8'
        }
    )

    r = SESSION.post(
        url=PAYCONIQ_PAYMENT_PROFILES_URL,
        json={
            'size': 300
        }
    )

    r.raise_for_status()

    return {
        'session': SESSION,
        'payment_profile_id_sticker': [item['paymentProfileId'] for item in r.json()['content'] if item['productName'] == 'ON_STICKER_NON_INTEGRATED'][0],
        'payment_profile_id_app_to_app': [item['paymentProfileId'] for item in r.json()['content'] if item['productName'] == 'APP2APP_INTEGRATED'][0]
    }


def get_totals_from_payment_profile_id(SESSION: requests.Session, payment_profile_id: str):

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    today = datetime.datetime.today()

    day = today.strftime('%Y-%m-%dT00:00:00Z')

    start_of_week = (today - datetime.timedelta(
        days=today.weekday())).strftime('%Y-%m-%dT00:00:00Z')

    start_of_month = (today - datetime.timedelta(
        days=today.day-1)).strftime('%Y-%m-%dT00:00:00Z')

    start_of_year = datetime.datetime(
        today.year, 1, 1).strftime('%Y-%m-%dT00:00:00Z')

    r = SESSION.post(
        url=PAYCONIQ_TOTALS_URL,
        json={
            "paymentsTotalRequest":
                [
                    {
                        "intervalType": "DAY",
                        "timeInterval":
                        {
                            "from": day,
                            "to": now
                        }
                    },
                    {
                        "intervalType": "WEEK",
                        "timeInterval":
                        {
                            "from": start_of_week,
                            "to": now
                        }
                    },
                    {
                        "intervalType": "MONTH",
                        "timeInterval":
                        {
                            "from": start_of_month,
                            "to": now
                        }
                    },
                    {
                        "intervalType": "YEAR",
                        "timeInterval":
                        {
                            "from": start_of_year,
                            "to": now
                        }
                    }],
            "accountId": payment_profile_id
        }
    )

    r.raise_for_status()

    totals_json = r.json()['paymentsTotal']

    for index, total in enumerate(totals_json):

        total['intervalType'] = TOTAL_SUMMARIES[index]

    return totals_json



