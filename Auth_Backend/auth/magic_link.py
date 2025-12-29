from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_magic_token(email: str, purpose: str):
    return jwt.encode(
        {
            "sub": email,
            "purpose": purpose,
            "exp": datetime.utcnow() + timedelta(minutes=10)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_magic_token(token: str, purpose: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    if payload.get("purpose") != purpose:
        raise HTTPException(400, "Invalid token purpose")

    return payload