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
├── LICENSE                   # Custom restrictive license
├── README.md                 # Project documentation
├── main.py                   # main orchestrator file
├── credentials.json       # OAuth client credentials (gitignored or shared securely)
└── tests/                    # Unit and integration tests
    ├── test_fetch.py          # Tests for fetch_store_emails
    ├── test_process.py        # Tests for process_rules
    └── test_db.py             # Tests for db and models

---

## ⚙️ Setup Instructions

Follow these steps to get the project running on your local machine:

### Step 1: Install Python (using pyenv recommended)

- Install `pyenv` (macOS example):

  ```bash
  brew install pyenv
  pyenv install 3.8.18
  pyenv local 3.8.18
  python -m venv venv
  source venv/bin/activate

  NOTE : Ignore python 3.8 is installed

### Step 2: Install Python dependencies 
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

### Step 3: Enable Gmail API and create OAuth credentials

You will:

1. Go to the [Google Cloud Console](https://console.cloud.google.com).  
2. Create a **new project** or select an existing one.  
3. Navigate to **APIs & Services > Library** and **enable the Gmail API** for your project.  
4. Go to **APIs & Services > OAuth consent screen**.  
   - Choose the **User Type** — for personal or small app testing, select **External** (default).  
   - Fill out the required fields on the consent screen form:  
     - **App name:** A user-friendly name (e.g., “Gmail Smart Mail Processor”).  
     - **User support email:** Your email or your team’s email.  
     - **Developer contact email:** Your email (Google may use this to contact you).  
   - Scroll down to the **Test users** section:  
     - Add the email addresses that will be allowed to test the app.  
     - **Important:** Include your own Gmail address and any collaborators or recruiters who will use the app.  
     - If you don’t add your email here, the OAuth flow will fail with a consent error because the app is in testing mode and restricted to test users only.  

   > **Note:** If you don’t add your email as a test user, authentication will fail during the OAuth flow.  

5. Go to **APIs & Services > Credentials** and click **Create Credentials**.  
6. Choose **OAuth client ID** and select **Desktop app** as the application type.  
7. Name your client (e.g., "Gmail Smart Mail Processor") and click **Create**.  
8. Download the generated `credentials.json` file.  
9. Place the `credentials.json` file in the root directory of this project. 
   > Note : DO NOT USE A DIFFERENT NAME FOR `credentials.json` FILE


### Step 4: clone repo and run the script
 > Note : there is a sample rules.JSON file in the repository , please update it with repect to your gmail inbox to test

  ```bash
  git clone https://github.com/shalini1799/Gmail_Smart_Mail_Processor.git
  cd Gmail_Smart_Mail_Processor
  python main.py

## License
This repository is provided exclusively for HappyFox assignment evaluation.  
See [LICENSE](./LICENSE) for details.






