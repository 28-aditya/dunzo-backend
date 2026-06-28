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


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (ExpiredSignatureError, InvalidTokenError):
        return None


def hash_password(password: str) -> str:
    """Simple SHA-256 + salt hash. Use bcrypt in production."""
    salt = os.getenv("PASSWORD_SALT", "dunzo-default-salt")
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)