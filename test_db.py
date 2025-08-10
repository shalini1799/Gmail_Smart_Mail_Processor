import sqlite3
import pytest
import sys
import os

# Add the project root to sys.path to import db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import init_db, store_emails

@pytest.fixture
def in_memory_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_init_db_creates_table(in_memory_conn):
    # Pass in-memory connection to init_db
    init_db(conn=in_memory_conn)
    cursor = in_memory_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails';")
    assert cursor.fetchone() is not None

def test_store_emails_inserts_new_email(in_memory_conn):
    init_db(conn=in_memory_conn)
    emails = [{
        "id": "email1",
        "sender": "alice@example.com",
        "subject": "Hello",
        "snippet": "Hi there!",
        "labels": "INBOX",
        "internal_date": "2025-08-10T12:00:00Z"
    }]
    store_emails(emails, conn=in_memory_conn)
    cursor = in_memory_conn.cursor()
    cursor.execute("SELECT * FROM emails WHERE id=?", ("email1",))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "email1"
    assert row[1] == "alice@example.com"
    assert row[2] == "Hello"

def test_store_emails_skips_existing_email(in_memory_conn):
    init_db(conn=in_memory_conn)
    emails = [{
        "id": "email1",
        "sender": "alice@example.com",
        "subject": "Hello",
        "snippet": "Hi there!",
        "labels": "INBOX",
        "internal_date": "2025-08-10T12:00:00Z"
    }]
    store_emails(emails, conn=in_memory_conn)
    # Insert again; should skip as email already exists
    store_emails(emails, conn=in_memory_conn)
    cursor = in_memory_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emails WHERE id=?", ("email1",))
    count = cursor.fetchone()[0]
    assert count == 1