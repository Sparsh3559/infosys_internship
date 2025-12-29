from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXP_MINUTES = 10

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")


def create_magic_token(email: str, purpose: str) -> str:
    """
    Creates a short-lived JWT for:
    - email verification
    - login magic link
    """

    payload = {
        "sub": email,
        "purpose": purpose,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXP_MINUTES),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_magic_token(token: str, purpose: str) -> dict:
    """
    Verifies token validity, expiry, and purpose
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

    if payload.get("purpose") != purpose:
        raise HTTPException(
            status_code=400,
            detail="Invalid token purpose"
        )

    return payload