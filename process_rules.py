import json
import sqlite3
import logging
from db import DB_FILE
from fetch_store_emails import get_or_create_label

logger = logging.getLogger(__name__)
RULES_FILE = 'rules.json'

def load_rules():
    logger.info(f"Loading rules from {RULES_FILE}...")
    with open(RULES_FILE, 'r') as f:
        rules = json.load(f)
    logger.info(f"Loaded {len(rules)} rules.")
    return rules

def match_rule(email, rule):

    conditions = rule.get('conditions', {})
    predicate = rule.get('predicate', 'All').lower()

    checks = []

    # Check 'from' conditions if present
    if 'from' in conditions:
        checks.append(any(f.lower() in email['sender'].lower() for f in conditions['from']))
    else:
        # If no 'from' condition, consider it matched by default
        checks.append(True)

    # Check 'subject_contains' conditions if present
    if 'subject_contains' in conditions:
        checks.append(any(s.lower() in email['subject'].lower() for s in conditions['subject_contains']))
    else:
        # If no subject_contains condition, consider it matched by default
        checks.append(True)

    if predicate == 'all':
        return all(checks)
    elif predicate == 'any':
        return any(checks)
    else:
        logger.warning(f"Unknown predicate '{rule.get('predicate')}', defaulting to 'All'")
        return all(checks)

def apply_rules(service, conn):
    rules = load_rules()

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails WHERE is_read=0 AND processed=0")
    emails = cursor.fetchall()

    logger.info(f"Applying rules to {len(emails)} unread emails...")
    processed_count = 0

    for email in emails:
        email_id, sender, subject, snippet, labels, internal_date, is_read, processed = email
        email_dict = {
            "id": email_id,
            "sender": sender,
            "subject": subject,
            "snippet": snippet,
            "labels": labels
        }

        for rule in rules:
            if match_rule(email_dict, rule):
                add_labels = []
                remove_labels = []

                if rule['actions'].get('mark_as_read'):
                    remove_labels.append("UNREAD")
                if 'label' in rule['actions']:
                    label_id = get_or_create_label(service, rule['actions']['label'])
                    add_labels.append(label_id)

                service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={
                        "removeLabelIds": remove_labels,
                        "addLabelIds": add_labels
                    }
                ).execute()

                new_labels_str = labels
                if 'label' in rule['actions']:
                    new_labels_str += ',' + rule['actions']['label']
                if "UNREAD" in new_labels_str:
                    new_labels_str = new_labels_str.replace("UNREAD", "")
                cursor.execute("""
                    UPDATE emails SET labels=?, is_read=1, processed=1 WHERE id=?
                """, (new_labels_str, email_id))
                conn.commit()

                logger.info(f"Email '{subject}' from '{sender}' matched rule '{rule['name']}'. Applied label '{rule['actions'].get('label')}' and marked as read.")
                processed_count += 1

    logger.info(f"Finished applying rules. Total emails processed: {processed_count}")