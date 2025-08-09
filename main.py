from fetch_store_emails import fetch_and_store_emails, get_gmail_service
from process_rules import match_email, apply_actions, process_email, RULES
from db import load_emails_from_db
from db import engine, Base
from model import Email

def main():
    # Step 1: Fetch latest emails and store them in DB
    print("Fetching and storing emails...")
    fetch_and_store_emails()

    # Step 2: Authenticate Gmail API client with modify scope
    print("Authenticating Gmail API with modify scope...")
    service = get_gmail_service() 

    # Step 3: Load emails from DB
    print("Loading stored emails from database...")
    stored_emails = load_emails_from_db()

    # Step 4: Process each email with rules and apply actions
    print("Processing emails based on rules...")
    for email in stored_emails:
        process_email(service, email)

if __name__ == '__main__':
    # Create tables on first run if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    main()