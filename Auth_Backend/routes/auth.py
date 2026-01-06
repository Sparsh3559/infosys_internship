from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import os
import urllib.parse

from Auth_Backend.database import SessionLocal
from Auth_Backend.models import User
from Auth_Backend.auth.magic_link import create_magic_token, verify_magic_token
from Auth_Backend.auth.jwt import create_jwt
from Auth_Backend.auth.email import send_magic_link

router = APIRouter()

# --------------------------------------------------
# ENVIRONMENT VARIABLES
# --------------------------------------------------
APP_URL = os.getenv("APP_URL")              # Backend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")    # Streamlit App URL

if not APP_URL or not FRONTEND_URL:
    raise RuntimeError("APP_URL or FRONTEND_URL not set")

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
# REGISTER
# --------------------------------------------------
@router.post("/register")
def register(name: str, email: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=name,
        email=email,
        is_verified=False
    )
    db.add(user)
    db.commit()

    token = create_magic_token(email, "verify")
    verify_link = f"{APP_URL}/verify?token={token}"

    send_magic_link(email, verify_link, "verify")

    return {"message": "Verification email sent"}

# --------------------------------------------------
# VERIFY EMAIL
# --------------------------------------------------
@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = verify_magic_token(token, "verify")
        email = payload["sub"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    return RedirectResponse(
        url=f"{FRONTEND_URL}/Verify?status=verified",
        status_code=302
    )

# --------------------------------------------------
# LOGIN (MAGIC LINK)
# --------------------------------------------------
@router.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    token = create_magic_token(email, "login")
    login_link = f"{APP_URL}/login/verify?token={token}"

    send_magic_link(email, login_link, "login")

    return {"message": "Login link sent"}

# --------------------------------------------------
# VERIFY LOGIN → ISSUE JWT → REDIRECT TO FRONTEND
# --------------------------------------------------
@router.get("/login/verify")
def verify_login(token: str):
    try:
        payload = verify_magic_token(token, "login")
        email = payload["sub"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    jwt_token = create_jwt(email)
    encoded_jwt = urllib.parse.quote(jwt_token)

    return RedirectResponse(
        url=f"{FRONTEND_URL}/Verify?jwt={encoded_jwt}&email={email}",
        status_code=302
    )