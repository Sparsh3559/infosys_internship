from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth.magic_link import create_magic_token, verify_magic_token
from auth.jwt import create_jwt
from auth.email import send_magic_link

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(400, "User already exists")

    user = User(name=name, email=email)
    db.add(user)
    db.commit()

    token = create_magic_token(email)
    link = f"http://localhost:8000/verify?token={token}"
    send_magic_link(email, link)

    return {"message": "Verification email sent"}

@router.get("/verify")
def verify(token: str, db: Session = Depends(get_db)):
    payload = verify_magic_token(token)
    email = payload["sub"]

    user = db.query(User).filter(User.email == email).first()
    user.is_verified = True
    db.commit()

    jwt_token = create_jwt(email)
    return {"token": jwt_token}