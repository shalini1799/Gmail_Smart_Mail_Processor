import os
import pytest
from unittest.mock import patch, MagicMock
from unittest.mock import patch, mock_open
from fetch_store_emails import gmail_authenticate, fetch_top_emails, get_or_create_label

# -- gmail_authenticate tests --

@patch("fetch_store_emails.os.path.exists")
@patch("fetch_store_emails.Credentials.from_authorized_user_file")
@patch("fetch_store_emails.InstalledAppFlow")
@patch("fetch_store_emails.build")
def test_gmail_authenticate_token_exists_valid(
    mock_build, mock_flow, mock_cred_from_file, mock_path_exists
):
    # Token file exists and credentials valid
    mock_path_exists.return_value = True
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_cred_from_file.return_value = mock_creds

    mock_build.return_value = "service-object"

    service = gmail_authenticate()

    mock_cred_from_file.assert_called_once()
    mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
    assert service == "service-object"

@patch("fetch_store_emails.os.path.exists")
@patch("fetch_store_emails.Credentials.from_authorized_user_file")
@patch("fetch_store_emails.InstalledAppFlow")
@patch("fetch_store_emails.build")
def test_gmail_authenticate_token_missing_or_invalid(
    mock_build, mock_flow_class, mock_cred_from_file, mock_path_exists, tmp_path
):
    # Token file exists but creds invalid, so OAuth flow triggers

    mock_path_exists.return_value = True

    # creds from file is invalid
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_cred_from_file.return_value = mock_creds

    # Mock InstalledAppFlow instance & run_local_server
    mock_flow = MagicMock()
    mock_flow.run_local_server.return_value = MagicMock()
    mock_flow_class.from_client_secrets_file.return_value = mock_flow

    # Mock creds.to_json()
    mock_flow.run_local_server.return_value.to_json.return_value = '{"token": "fake"}'

    mock_build.return_value = "service-object"

    # Patch open to prevent actual file write
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        service = gmail_authenticate()

    mock_flow_class.from_client_secrets_file.assert_called_once()
    mock_flow.run_local_server.assert_called_once()
    mock_build.assert_called_once()
    assert service == "service-object"

# -- fetch_top_emails tests --

def test_fetch_top_emails_returns_emails():
    # Mock service with nested calls returning a dummy email list
    mock_service = MagicMock()

    # Setup list().execute() chain
    mock_service.users().messages().list().execute.return_value = {
        'messages': [{'id': '123'}]
    }

    # Setup get().execute() chain
    mock_service.users().messages().get().execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'alice@example.com'},
                {'name': 'Subject', 'value': 'Test Email'}
            ]
        },
        'snippet': 'This is a test',
        'labelIds': ['INBOX', 'IMPORTANT'],
        'internalDate': '1691664000000'  # corresponds to some timestamp
    }

    emails = fetch_top_emails(mock_service, max_results=1)

    assert len(emails) == 1
    email = emails[0]
    assert email['id'] == '123'
    assert email['sender'] == 'alice@example.com'
    assert email['subject'] == 'Test Email'
    assert email['snippet'] == 'This is a test'
    assert 'INBOX' in email['labels']
    assert 'IMPORTANT' in email['labels']
    assert email['internal_date']  # check string present

# -- get_or_create_label tests --

def test_get_or_create_label_existing_label():
    mock_service = MagicMock()
    # Mock labels().list().execute() returns a label that matches
    mock_service.users().labels().list().execute.return_value = {
        'labels': [{'id': 'LABEL_1', 'name': 'TestLabel'}]
    }

    label_id = get_or_create_label(mock_service, 'TestLabel')

    assert label_id == 'LABEL_1'

def test_get_or_create_label_creates_new_label():
    mock_service = MagicMock()
    # No existing label found
    mock_service.users().labels().list().execute.return_value = {
        'labels': [{'id': 'LABEL_1', 'name': 'OtherLabel'}]
    }
    # Mock create().execute() returns new label
    mock_service.users().labels().create().execute.return_value = {
        'id': 'NEW_LABEL_ID'
    }

    label_id = get_or_create_label(mock_service, 'NewLabel')

    assert label_id == 'NEW_LABEL_ID'