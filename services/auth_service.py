from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from db.models import RefreshToken, User
from core.security import (
    generate_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
)
from utils.helpers import utc_now

REFRESH_TOKEN_TTL_DAYS = 30


def _parse_refresh_token(raw_token: str) -> tuple[UUID, str] | None:
    if not raw_token or raw_token.count(".") != 1:
        return None

    token_id_str, secret = raw_token.split(".", 1)
    try:
        return UUID(token_id_str), secret
    except ValueError:
        return None


def _get_valid_refresh_record(
    db: Session, raw_token: str
) -> RefreshToken | None:
    parsed = _parse_refresh_token(raw_token)
    if not parsed:
        return None

    token_id, secret = parsed
    record = db.query(RefreshToken).filter(
        RefreshToken.id == token_id,
        RefreshToken.revoked == False,
    ).first()

    if not record or record.expires_at < utc_now():
        return None

    if not verify_refresh_token(secret, record.token_hash):
        return None

    return record


def issue_refresh_token(
    db: Session, user_id, expires_days: int = REFRESH_TOKEN_TTL_DAYS
) -> str:
    """Creates a new refresh token, stores its bcrypt hash, and returns
    ``{token_id}.{secret}`` for the cookie. The raw secret is never persisted."""
    raw_secret = generate_refresh_token()
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_secret),
        expires_at=utc_now() + timedelta(days=expires_days),
    )
    db.add(record)
    db.flush()
    db.commit()

    return f"{record.id}.{raw_secret}"


def get_user_from_refresh_token(db: Session, raw_token: str) -> User | None:
    record = _get_valid_refresh_record(db, raw_token)
    if not record:
        return None

    return db.query(User).filter(User.id == record.user_id).first()


def rotate_refresh_token(
    db: Session, raw_token: str
) -> tuple[User, str, int] | None:
    record = _get_valid_refresh_record(db, raw_token)
    if not record:
        return None

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        return None

    remaining_days = max(1, (record.expires_at - utc_now()).days)

    record.revoked = True
    db.commit()

    new_token = issue_refresh_token(db, user.id, expires_days=remaining_days)
    return user, new_token, remaining_days


def revoke_refresh_token(db: Session, raw_token: str):
    record = _get_valid_refresh_record(db, raw_token)
    if not record:
        return

    record.revoked = True
    db.commit()
