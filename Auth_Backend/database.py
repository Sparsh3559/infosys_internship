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
        # ✅ FIXED: Use absolute import
        from Auth_Backend.models import User, ContentHistory
        
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

# --------------------------------------------------
# AUTO-INITIALIZE ON IMPORT
# --------------------------------------------------
# Automatically create tables when this module is imported
if not os.path.exists("users.db"):
    print("📦 Database not found. Creating new database...")
    init_db()
else:
    print("✅ Database connection established.")