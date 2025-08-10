import json
import sqlite3
import logging
from datetime import datetime, timedelta
from dateutil.parser import parse
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

def match_condition(email, condition):
    field = condition['field'].lower()
    predicate = condition['predicate'].lower()
    value = condition['value']

    # Extract email field value safely, default empty string if missing
    email_val = email.get(field, "")

    # For 'received' field, parse date from email
    if field == "received":
        try:
            # Assuming email['received'] is a string date, parse it
            email_date = parse(email_val)
        except Exception as e:
            logger.warning(f"Invalid date format in email: {email_val}")
            return False

        # value is number of days (int)
        if predicate == "less_than_days":
            return (datetime.now() - email_date) < timedelta(days=int(value))
        elif predicate == "greater_than_days":
            return (datetime.now() - email_date) > timedelta(days=int(value))
        else:
            logger.warning(f"Unknown predicate for date: {predicate}")
            return False

    # For string fields
    email_val_lower = str(email_val).lower()
    value_lower = str(value).lower()

    if predicate == "contains":
        return value_lower in email_val_lower
    elif predicate == "does_not_contain":
        return value_lower not in email_val_lower
    elif predicate == "equals":
        return email_val_lower == value_lower
    elif predicate == "does_not_equal":
        return email_val_lower != value_lower
    else:
        logger.warning(f"Unknown predicate '{predicate}' in condition")
        return False

def match_rule(email, rule):
    conditions = rule.get('conditions', [])
    rule_predicate = rule.get('predicate', 'All').lower()

    if not conditions:
        return True  # no conditions means match everything

    results = [match_condition(email, cond) for cond in conditions]

    if rule_predicate == "all":
        return all(results)
    elif rule_predicate == "any":
        return any(results)
    else:
        logger.warning(f"Unknown rule predicate '{rule_predicate}', defaulting to all")
        return all(results)

def apply_rules(service, conn):
    rules = load_rules()

    cursor = conn.cursor()
    cursor.execute("SELECT id, sender, subject, snippet, labels, internal_date, is_read, processed FROM emails WHERE is_read=0 AND processed=0")
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
            "labels": labels,
            "received": internal_date  # Add received date for date predicates
        }

        for rule in rules:
            if match_rule(email_dict, rule):
                add_labels = []
                remove_labels = []

                # Mark as read/unread action
                if rule['actions'].get('mark_as_read') is True:
                    remove_labels.append("UNREAD")
                elif rule['actions'].get('mark_as_read') is False:
                    add_labels.append("UNREAD")

                # Move message (apply label)
                label_name = rule['actions'].get('move_to_folder') or rule['actions'].get('label')
                label_id = None
                if label_name:
                    label_name = label_name.strip()
                    if label_name:
                        try:
                            label_id = get_or_create_label(service, label_name)
                            add_labels.append(label_id)
                        except Exception as e:
                            logger.error(f"Failed to create or get label '{label_name}': {e}")
                    else:
                        logger.warning(f"Skipping empty label name in rule '{rule['name']}'")
                else:
                    logger.debug(f"No label to apply for rule '{rule['name']}'")

                service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={
                        "removeLabelIds": remove_labels,
                        "addLabelIds": add_labels
                    }
                ).execute()

                # Update DB labels string (add label name, remove UNREAD if marked read)
                new_labels_str = labels
                if label_name and label_id:
                    if label_name not in new_labels_str.split(','):
                        new_labels_str += ',' + label_name
                if "UNREAD" in new_labels_str and "UNREAD" in remove_labels:
                    new_labels_str = new_labels_str.replace("UNREAD", "")
                elif "UNREAD" in add_labels:
                    if "UNREAD" not in new_labels_str:
                        new_labels_str += ",UNREAD"

                cursor.execute("""
                    UPDATE emails SET labels=?, is_read=?, processed=1 WHERE id=?
                """, (new_labels_str.strip(','), 1 if rule['actions'].get('mark_as_read') else 0, email_id))
                conn.commit()

                logger.info(f"Email '{subject}' from '{sender}' matched rule '{rule['name']}'. Applied label '{label_name}' and marked as read: {rule['actions'].get('mark_as_read')}.")
                processed_count += 1

    logger.info(f"Finished applying rules. Total emails processed: {processed_count}")