import pytest
from unittest import mock
from unittest.mock import patch, MagicMock, mock_open
import process_rules  # import your module under test

@patch("builtins.open", new_callable=mock_open, read_data='[{"name":"rule1"}]')
@patch("json.load")
def test_load_rules(mock_json_load, mock_file):
    mock_json_load.return_value = [{"name": "rule1"}]
    rules = process_rules.load_rules()
    assert isinstance(rules, list)
    assert rules[0]["name"] == "rule1"
    mock_file.assert_called_once_with(process_rules.RULES_FILE, 'r')  # Fixed to expect mode 'r'

def test_match_rule_all_conditions():
    email = {"sender": "alice@example.com", "subject": "Hello World"}
    rule = {
        "predicate": "All",
        "conditions": {
            "from": ["alice"],
            "subject_contains": ["hello"]
        }
    }
    assert process_rules.match_rule(email, rule) is True

def test_match_rule_any_conditions():
    email = {"sender": "bob@example.com", "subject": "Special Offer"}
    rule = {
        "predicate": "Any",
        "conditions": {
            "from": ["alice", "bob"],
            "subject_contains": ["discount"]
        }
    }
    # sender matches "bob", so True even if subject doesn't match
    assert process_rules.match_rule(email, rule) is True

def test_match_rule_no_conditions_defaults_true():
    email = {"sender": "someone@example.com", "subject": "No rules"}
    rule = {}
    assert process_rules.match_rule(email, rule) is True

def test_match_rule_unknown_predicate_logs_warning(monkeypatch):
    email = {"sender": "alice", "subject": "hello"}
    rule = {"predicate": "unknown", "conditions": {"from": ["alice"]}}
    logs = []

    # Patch the logger.warning used in the module
    monkeypatch.setattr(process_rules.logger, "warning", lambda msg: logs.append(msg))

    assert process_rules.match_rule(email, rule) is True
    assert any("Unknown predicate" in msg for msg in logs)

@patch("process_rules.load_rules")
@patch("sqlite3.connect")
def test_apply_rules(mock_connect, mock_load_rules):
    # Setup mock rules
    mock_load_rules.return_value = [
        {
            "name": "Mark Read and Label",
            "conditions": {"from": ["alice"]},
            "predicate": "All",
            "actions": {"mark_as_read": True, "label": "TestLabel"}
        }
    ]

    # Setup mock DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Fake emails returned from DB - tuple: (id, sender, subject, snippet, labels, internal_date, is_read, processed)
    mock_cursor.fetchall.return_value = [
        ("email1", "alice@example.com", "Hello", "snippet", "INBOX,UNREAD", "2025-08-10", 0, 0),
        ("email2", "bob@example.com", "Hi", "snippet", "INBOX", "2025-08-10", 0, 0)
    ]

    # Mock service and its chain of calls
    mock_service = MagicMock()
    mock_modify = MagicMock()
    mock_service.users().messages().modify.return_value = mock_modify
    mock_modify.execute.return_value = None

    # Patch get_or_create_label to return a fake label id
    with patch("process_rules.get_or_create_label", return_value="LabelID123"):
        process_rules.apply_rules(mock_service)

    # Validate DB queries and commits called at least once
    mock_cursor.execute.assert_any_call("SELECT * FROM emails WHERE is_read=0 AND processed=0")
    assert mock_conn.commit.call_count >= 1

    # Validate that modify API called once for matched email only (email1 from alice)
    mock_service.users().messages().modify.assert_called_once_with(
        userId='me',
        id="email1",
        body={
            "removeLabelIds": ["UNREAD"],
            "addLabelIds": ["LabelID123"]  # label id returned by mocked get_or_create_label
        }
    )