from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base  
from model import Email

DATABASE_URL = "sqlite:///emails.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
def load_emails_from_db():
    db = SessionLocal()
    try:
        emails = db.query(Email).all()
        email_dicts = []
        for email_obj in emails:
            email_dicts.append({
                'id': email_obj.id,
                'sender': email_obj.sender or '',
                'subject': email_obj.subject or '',
                'received_at': email_obj.received_at,  # datetime object with tzinfo if set
                'snippet': email_obj.snippet or '',
                # If you have labels in DB, add here, else empty list
                'labels': []
            })
        return email_dicts
    finally:
        db.close()        