from sqlalchemy import Column, Integer, String, DateTime, Text
from base import Base

class Email(Base):
    __tablename__ = "emails"   

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    received_at = Column(DateTime(timezone=True), nullable=True, index=True)
    snippet = Column(Text)       # email content