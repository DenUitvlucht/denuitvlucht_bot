
import requests
import os
import uuid

from dotenv import load_dotenv

from data.json_helper import read_from_json, write_to_json

load_dotenv()

SUMUP_ID = os.getenv('SUMUP_ID')
SUMUP_SECRET = os.getenv('SUMUP_SECRET')

SUMUP_AUTH_URL = 'https://api.sumup.com/authorize'
SUMUP_TOKEN_URL = 'https://api.sumup.com/token'
SUMUP_PROFILE_URL = 'https://api.sumup.com/v0.1/me/merchant-profile/doing-business-as'
SUMUP_TRANSACTIONS_URL = 'https://me.sumup.com/api/proxy/v0.1/me/analytics'

SUMUP_JSON = os.path.join(
    os.getcwd(), 'sumup_token.json')


def auth():

    SESSION = requests.Session()

    SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
    })

    r = SESSION.get(
        url=SUMUP_AUTH_URL,
        params={
            'response_type': 'code',
            'client_id': SUMUP_ID,
            'redirect_uri': 'https://denuitvlucht.com/oauth2',
            'scope': 'transactions.history user.profile_readonly',
            'state': uuid.uuid4()
        },
    )

    return r.url


def get_refresh_token(code: str):

    SESSION = requests.Session()

    SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    r = SESSION.post(
        url=SUMUP_TOKEN_URL,
        data={
            'response_type': 'code',
            'grant_type': 'authorization_code',
            'client_id': SUMUP_ID,
            'client_secret': SUMUP_SECRET,
            'code': code
        },
    )

    r.raise_for_status()

    token_json = read_from_json(path=SUMUP_JSON)
    token_json['refresh_token'] = r.json()['refresh_token']
    write_to_json(path=SUMUP_JSON, data=token_json)

    return r.json()['refresh_token']


def get_access_token():

    SESSION = requests.Session()

    SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    refresh_token = read_from_json(path=SUMUP_JSON)['refresh_token']

    r = SESSION.post(
        url=SUMUP_TOKEN_URL,
        data={
            'response_type': 'code',
            'grant_type': 'refresh_token',
            'client_id': SUMUP_ID,
            'client_secret': SUMUP_SECRET,
            'refresh_token': refresh_token
        },
    )

    return r.json()['access_token']


def get_sumup_transactions(access_token: str, start_date: str, end_date: str):

    SESSION = requests.Session()
    SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    })

    r = SESSION.get(
        url=SUMUP_TRANSACTIONS_URL,
        params={
            'start_date': start_date,
            'end_date': end_date,
            'resolution': 'daily',
            'bow': 'sun',
            'country': 'be'
        }
    )

    r.raise_for_status()

    return {
        'revenue': r.json()['total']['amount'],
        'transaction_count': r.json()['total']['count']
    }
