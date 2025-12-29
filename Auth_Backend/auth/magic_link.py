from datetime import datetime, timedelta
from jose import jwt

MAGIC_SECRET = "MAGIC_LINK_SECRET"
ALGORITHM = "HS256"

if not MAGIC_SECRET:
    raise RuntimeError("MAGIC_LINK_SECRET environment variable not set")

def create_magic_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    return jwt.encode(payload, MAGIC_SECRET, algorithm=ALGORITHM)

def verify_magic_token(token: str):
    return jwt.decode(token, MAGIC_SECRET, algorithms=[ALGORITHM])