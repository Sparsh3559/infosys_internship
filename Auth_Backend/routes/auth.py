from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from database import SessionLocal
from models import User
from auth.magic_link import create_magic_token, verify_magic_token
from auth.jwt import create_jwt
from auth.email import send_magic_link

router = APIRouter()

# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------
APP_URL = os.getenv("APP_URL")  # e.g. https://infosys-internship-backend.onrender.com

if not APP_URL:
    raise RuntimeError("APP_URL environment variable is not set")

# --------------------------------------------------
# DATABASE DEPENDENCY
# --------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# REGISTER (FIRST-TIME USER)
# --------------------------------------------------
@router.post("/register")
def register(name: str, email: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=name,
        email=email,
        is_verified=False
    )
    db.add(user)
    db.commit()

    token = create_magic_token(email=email, purpose="verify")
    verify_link = f"{APP_URL}/verify?token={token}"

    # ✅ FIXED: positional args only
    send_magic_link(
        email,
        verify_link,
        "verify"
    )

    return {
        "message": "Verification email sent. Please check your inbox."
    }

# --------------------------------------------------
# LOGIN (MAGIC LINK)
# --------------------------------------------------
@router.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    token = create_magic_token(email=email, purpose="login")
    login_link = f"{APP_URL}/login/verify?token={token}"

    # ✅ FIXED
    send_magic_link(
        email,
        login_link,
        "login"
    )

    return {
        "message": "Login link sent. Please check your email."
    }

# --------------------------------------------------
# VERIFY EMAIL (FROM REGISTER MAIL)
# --------------------------------------------------
@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = verify_magic_token(token, purpose="verify")
        email = payload["sub"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified. Please log in."}

    user.is_verified = True
    db.commit()

    return {
        "message": "Email verified successfully. You can now log in."
    }

# --------------------------------------------------
# VERIFY LOGIN (ISSUE JWT)
# --------------------------------------------------
@router.get("/login/verify")
def verify_login(token: str):
    try:
        payload = verify_magic_token(token, purpose="login")
        email = payload["sub"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    jwt_token = create_jwt(email)

    return {
        "jwt": jwt_token,
        "email": email
    }