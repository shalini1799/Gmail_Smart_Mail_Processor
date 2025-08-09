import os
import pickle
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from db import SessionLocal
from model import Email
from email.utils import parsedate_to_datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_api_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def fetch_and_store_emails():
    service = get_gmail_service()
    db = SessionLocal()

    try:
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])

        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()

            headers = msg_detail['payload']['headers']
            sender = subject = date_received = None

            for header in headers:
                name = header['name'].lower()
                if name == 'from':
                    sender = header['value']
                elif name == 'subject':
                    subject = header['value']
                elif name == 'date':
                    date_received = parsedate_to_datetime(header['value'])
                    if date_received is not None:
                        if date_received.tzinfo is None:
                            date_received = date_received.replace(tzinfo=timezone.utc)

            snippet = msg_detail.get('snippet', '')

            email_entry = Email(
                sender=sender,
                subject=subject,
                received_at=date_received,
                snippet=snippet
            )
            db.add(email_entry)

        db.commit()
        print(f"Stored {len(messages)} emails in the database.")

    finally:
        db.close()


if __name__ == '__main__':
    fetch_and_store_emails()