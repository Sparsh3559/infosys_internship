from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from fastapi import HTTPException

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
SESSION_EXP_HOURS = 2

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")


def create_jwt(email: str) -> str:
    payload = {
        "sub": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=SESSION_EXP_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")