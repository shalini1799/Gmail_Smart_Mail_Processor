import sqlite3
from db import init_db, store_emails
from fetch_store_emails import gmail_authenticate, fetch_top_emails
from process_rules import apply_rules
from config import logger, DB_FILE

if __name__ == '__main__':
    logger.info("Starting Gmail processor script...")

    # Open shared DB connection
    conn = sqlite3.connect(DB_FILE)

    # Pass connection to functions that use DB
    init_db(conn)
    service = gmail_authenticate()

    emails = fetch_top_emails(service)
    store_emails(emails, conn)

    apply_rules(service, conn)

    # Close the shared DB connection at the end
    conn.close()

    logger.info("Processing complete.")