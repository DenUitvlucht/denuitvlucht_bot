from __future__ import print_function

import base64
import mimetypes
import os

from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


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


def gmail_send_message_with_attachment(attachment: str, attachment_name: str, receiver: str, sender: str, subject: str, message: str):

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
        mime_message = EmailMessage()

        # headers
        mime_message['To'] = receiver
        mime_message['From'] = sender
        mime_message['Subject'] = subject

        # text
        mime_message.set_content(
            message
        )

        # attachment
        attachment_filename = attachment
        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(attachment_filename)
        maintype, subtype = type_subtype.split('/')

        with open(attachment_filename, 'rb') as fp:
            attachment_data = fp.read()
        mime_message.add_attachment(
            attachment_data, maintype, subtype, filename=attachment_name)

        encoded_message = base64.urlsafe_b64encode(
            mime_message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        # pylint: disable=E1101

        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())

    except HttpError as error:

        send_message = None

    return send_message
