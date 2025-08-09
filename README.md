# happy_fox_assignment

# 📧 Gmail Smart Mail Processor — Python Assignment

A standalone Python project that integrates with the **Gmail API** to:

1. Authenticate via OAuth 2.0.
2. Fetch emails from your inbox.
3. Store them in a relational database.
4. Process them based on **JSON-defined rules**.
5. Perform actions such as marking as read/unread or moving to another label.

---

## 📋 Features

- **OAuth 2.0 Gmail API authentication** using Google’s official Python client.
- Email fetching without IMAP (uses Gmail REST API).
- Store emails in PostgreSQL, MySQL, or SQLite3 (default).
- JSON-based rules with support for:
  - **String fields:** contains, does not contain, equals, does not equal
  - **Date fields:** less than / greater than (days/months)
- Actions:
  - Mark as read / unread
  - Move message to a specific label
- Rule set supports:
  - **All** — all conditions must match
  - **Any** — at least one condition must match
- Unit and integration test ready.

---

## 🗂 Project Structure

.
├── fetch_store_emails.py      # Script to authenticate and fetch emails
├── process_rules.py           # Script to process stored emails using JSON rules
├── rules.json                 # Sample rules file
├── db.py                      # Database connection and schema creation
├── models.py                  # SQLAlchemy models for Emails and Rules
├── requirements.txt           # Python dependencies
├── LICENSE                   # Custom restrictive license
├── README.md                 # Project documentation
├── main.py                   # main orchestrator file
├── gmail_api_creds.json       # OAuth client credentials (gitignored or shared securely)
└── tests/                    # Unit and integration tests
    ├── test_fetch.py          # Tests for fetch_store_emails
    ├── test_process.py        # Tests for process_rules
    └── test_db.py             # Tests for db and models

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites
- Python **3.8+**
- `pip` (Python package manager)
- Google Cloud project with **Gmail API enabled**
- Database:
  - PostgreSQL / MySQL (requires running DB server)
  - OR SQLite3 (default, no setup needed)

---

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/shalini1799/Gmail_Smart_Mail_Processor.git
cd Gmail_Smart_Mail_Processor

## License
This repository is provided exclusively for HappyFox assignment evaluation.  
See [LICENSE](./LICENSE) for details.