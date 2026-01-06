from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# --------------------------------------------------
# DATABASE CONFIG
# --------------------------------------------------
DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# --------------------------------------------------
# INITIALIZE DATABASE TABLES
# --------------------------------------------------
def init_db():
    """
    Create all database tables.
    This should be called once when the app starts.
    """
    try:
        # Try relative import first (for Streamlit), fall back to direct import (for FastAPI)
        try:
            from .models import User, ContentHistory
        except ImportError:
            from models import User, ContentHistory
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        return False

# --------------------------------------------------
# GET DATABASE SESSION
# --------------------------------------------------
def get_db():
    """
    Dependency to get database session.
    Use this in your routes/functions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()