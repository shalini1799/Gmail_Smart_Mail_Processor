import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES

logger = logging.getLogger(__name__)

def gmail_authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        logger.info("Loaded credentials from token file.")
    if not creds or not creds.valid:
        logger.info("No valid credentials found, starting OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        logger.info("OAuth flow complete and token saved.")
    return build('gmail', 'v1', credentials=creds)

def fetch_top_emails(service, max_results=5):
    logger.info(f"Fetching top {max_results} emails from Gmail inbox...")
    results = service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    email_data = []

    for msg in messages:
        full_msg = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = full_msg['payload']['headers']
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        snippet = full_msg.get('snippet', "")
        labels = ','.join(full_msg.get('labelIds', []))
        internal_date = datetime.fromtimestamp(int(full_msg['internalDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')

        email_data.append({
            'id': msg['id'],
            'sender': sender,
            'subject': subject,
            'snippet': snippet,
            'labels': labels,
            'internal_date': internal_date
        })
        logger.debug(f"Fetched email: {subject} from {sender}")

    logger.info(f"Fetched {len(email_data)} emails.")
    return email_data

def get_or_create_label(service, label_name):
    labels_list = service.users().labels().list(userId='me').execute().get('labels', [])
    for lbl in labels_list:
        if lbl['name'].lower() == label_name.lower():
            logger.debug(f"Found existing label '{label_name}' with id {lbl['id']}")
            return lbl['id']
    new_label = service.users().labels().create(
        userId='me',
        body={"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    ).execute()
    logger.info(f"Created new label '{label_name}' with id {new_label['id']}")
    return new_label['id']