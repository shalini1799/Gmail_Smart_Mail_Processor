from db import init_db, store_emails
from fetch_store_emails import gmail_authenticate, fetch_top_emails
from process_rules import apply_rules
from config import logger

if __name__ == '__main__':
    logger.info("Starting Gmail processor script...")
    init_db()
    service = gmail_authenticate()

    emails = fetch_top_emails(service)
    store_emails(emails)

    apply_rules(service)

    logger.info("Processing complete.")