from __future__ import print_function

import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def check_credentials():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return True

def get_message_attachment(location: list, queries: list):

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(
        userId='me', labelIds=location, q=queries).execute()

    messages = results.get('messages', [])
    
    if messages != []:

        for message in messages:

            msg = service.users().messages().get(
                userId='me', id=message['id']).execute()

            for part in msg['payload']['parts']:

                if part['partId'] == '1':

                    attachment_id = part['body']['attachmentId']
                    message_id = message['id']
            
    else:

        message_id, attachment_id = None, None

    return {
        'message_id': message_id,
        'attachment_id': attachment_id
    }

def get_attachment_data(message_id: str, attachment_id: str):

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    service = build('gmail', 'v1', credentials=creds)

    response = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()

    data = response['data']
    
    return base64.urlsafe_b64decode(data)


    

