from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from auth.magic_link import create_magic_token, verify_magic_token
from auth.jwt import create_jwt
from auth.email import send_magic_link

router = APIRouter()

# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# REGISTER (First-time user)
# -----------------------------
@router.post("/register")
def register(name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="User already registered"
        )

    user = User(
        name=name,
        email=email,
        is_verified=False
    )

    db.add(user)
    db.commit()

    token = create_magic_token(email)

    link = (
        "https://infosys-internship-backend.onrender.com"
        f"/verify?token={token}"
    )

    send_magic_link(email, link)

    return {
        "message": "Verification email sent"
    }


# -----------------------------
# LOGIN (Magic Link)
# -----------------------------
@router.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not registered"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )

    token = create_magic_token(email)

    link = (
        "https://infosys-internship-backend.onrender.com"
        f"/verify?token={token}"
    )

    send_magic_link(email, link)

    return {
        "message": "Magic login link sent"
    }


# -----------------------------
# VERIFY (Clicked from email)
# -----------------------------
@router.get("/verify")
def verify(token: str, db: Session = Depends(get_db)):
    try:
        payload = verify_magic_token(token)
        email = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.is_verified = True
    db.commit()

    jwt_token = create_jwt(email)

    # For internship demo: return JWT directly
    return {
        "message": "Email verified successfully",
        "jwt": jwt_token
    }