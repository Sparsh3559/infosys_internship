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
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    user = User(name=name, email=email, is_verified=False)
    db.add(user)
    db.commit()

    token = create_magic_token(email, purpose="verify")
    link = f"{APP_URL}/verify-email?token={token}"

    send_magic_link(email, link, purpose="verify")

    return {"message": "Verification email sent"}

# -----------------------------
# LOGIN (Magic Link)
# -----------------------------
@router.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    if not user.is_verified:
        raise HTTPException(400, "Email not verified")

    token = create_magic_token(email, purpose="login")
    link = f"{APP_URL}/login/verify?token={token}"

    send_magic_link(email, link, purpose="login")

    return {"message": "Login link sent"}

# -----------------------------
# VERIFY (Clicked from email)
# -----------------------------
@router.get("/verify")
def verify(token: str, db: Session = Depends(get_db)):
    try:
        payload = verify_magic_token(token, purpose="verify")
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

    if user.is_verified:
        return {"message": "Email already verified. Please log in."}

    user.is_verified = True
    db.commit()

    return {
        "message": "Email verified successfully. Please log in."
    }

@router.get("/login/verify")
def verify_login(token: str):
    payload = verify_magic_token(token, purpose="login")
    email = payload["sub"]

    jwt_token = create_jwt(email)

    return {
        "jwt": jwt_token,
        "email": email
    }