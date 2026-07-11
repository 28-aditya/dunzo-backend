import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import secrets
import hashlib
import bcrypt

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")


def create_token(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def create_access_token(user_id, minutes: int = 30) -> str:
    return create_token({
        "user_id": str(user_id),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp()),
    })


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def _hash_value(value: str) -> str:
    return bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode()


def _verify_hash(value: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(value.encode(), hashed.encode())
    except ValueError:
        return False


def hash_password(password: str) -> str:
    return _hash_value(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _verify_hash(password, password_hash)


# ─────────────────────────────────────────
# LEGACY SHA-256 PASSWORD MIGRATION
# ─────────────────────────────────────────

def is_legacy_password_hash(password_hash: str) -> bool:
    return not (password_hash or "").startswith(("$2a$", "$2b$", "$2y$"))


def verify_password_legacy_sha256(password: str, password_hash: str) -> bool:
    salt = os.getenv("PASSWORD_SALT", "dunzo-default-salt")
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == password_hash


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    return hashlib.sha256(token.encode()).hexdigest() == token_hash


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (ExpiredSignatureError, InvalidTokenError):
        return None


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)