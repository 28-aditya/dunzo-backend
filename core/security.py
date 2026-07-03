import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import secrets
import hashlib

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")


def create_token(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def create_access_token(user_id, minutes: int = 30) -> str:
    return create_token({
        "user_id": str(user_id),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp()),
    })


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (ExpiredSignatureError, InvalidTokenError):
        return None


def hash_password(password: str) -> str:
    salt = os.getenv("PASSWORD_SALT", "dunzo-default-salt")
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)