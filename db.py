import sqlite3
import logging
from config import DB_FILE

logger = logging.getLogger(__name__)

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            snippet TEXT,
            labels TEXT,
            internal_date TEXT,
            is_read INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0  
        )
        """)
        conn.commit()
    logger.info(f"Database initialized or already exists: {DB_FILE}")

def store_emails(email_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    count = 0
    for e in email_data:
        # Check if email already exists
        cursor.execute("SELECT processed FROM emails WHERE id=?", (e['id'],))
        row = cursor.fetchone()
        if row is None:
            # New email, insert with processed=0
            cursor.execute("""
                INSERT INTO emails (id, sender, subject, snippet, labels, internal_date, is_read, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (e['id'], e['sender'], e['subject'], e['snippet'], e['labels'], e['internal_date'], 0, 0))
            count += 1
        else:
            # Email exists, maybe update some fields but preserve processed flag
            # For simplicity, skip updating to preserve processed status
            pass
    conn.commit()
    conn.close()
    logger.info(f"Stored {count} new emails in database.")
