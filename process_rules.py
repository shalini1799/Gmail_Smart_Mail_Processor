import json
from datetime import datetime, timezone, timedelta

FIELD_MAP = {
    'From': 'sender',
    'Subject': 'subject',
    'Date received': 'received_at',
}

# Load all rules once at module load
with open('rules.JSON', 'r') as f:
    RULES = json.load(f) 

def check_predicate(field_value, predicate, value, unit=None):
    if not field_value:
        return False
    if isinstance(field_value, str):
        field_value_lower = field_value.lower()
    else:
        field_value_lower = field_value

    if predicate == 'contains':
        return value.lower() in field_value_lower
    elif predicate == 'less_than':
        if unit == 'days' and isinstance(field_value, datetime):
            now = datetime.now(timezone.utc)
            delta = timedelta(days=value)
            if field_value.tzinfo is None:
                field_value = field_value.replace(tzinfo=timezone.utc)
            return field_value >= (now - delta)
    return False

def match_email(email, rule):
    results = []
    for cond in rule['rules']:
        field_key = FIELD_MAP.get(cond['field'])
        if not field_key:
            print(f"Unknown field in rule: {cond['field']}")
            results.append(False)
            continue

        field_value = email.get(field_key, '')
        print(f"Checking field '{field_key}': value='{field_value}' predicate='{cond['predicate']}' against '{cond['value']}'")

        res = check_predicate(field_value, cond['predicate'], cond['value'], cond.get('unit'))
        print(f"Result: {res}")
        results.append(res)

    if rule['condition'].lower() == 'all':
        return all(results)
    else:
        return any(results)

def apply_actions(service, email, actions):
    msg_id = email['id']
    labels_to_add = []
    labels_to_remove = []

    for action in actions:
        if action['action'] == 'move_message' and action.get('target_mailbox', '').lower() == 'inbox':
            if 'INBOX' not in email.get('labels', []):
                labels_to_add.append('INBOX')
        if action['action'] == 'mark_as_read':
            if 'UNREAD' in email.get('labels', []):
                labels_to_remove.append('UNREAD')

    if labels_to_add or labels_to_remove:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={
                'addLabelIds': labels_to_add,
                'removeLabelIds': labels_to_remove
            }
        ).execute()
        print(f"Actions applied on message ID {msg_id}")

def process_email(service, email):

    matched_any = False
    for rule in RULES:
        if match_email(email, rule):
            print(f"Email '{email['subject']}' matched rule: {rule.get('description', 'No Description')}")
            apply_actions(service, email, rule['actions'])
            matched_any = True
    if not matched_any:
        print(f"Email '{email['subject']}' did not match any rule.")