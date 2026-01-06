from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from database import Base  
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)


class ContentHistory(Base):
    __tablename__ = "content_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)

    title = Column(String)
    content_type = Column(String)
    tone = Column(String)
    audience = Column(String)
    purpose = Column(String)
    word_limit = Column(Integer)

    generated_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)