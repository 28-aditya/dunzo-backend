from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from db.models import RefreshToken, User
from core.security import generate_refresh_token, hash_refresh_token

REFRESH_TOKEN_TTL_DAYS = 30


def issue_refresh_token(db: Session, user_id) -> str:
    """Creates a new refresh token, stores its hash, and returns the raw
    token to be set as a cookie. The raw value is never persisted."""
    raw_token  = generate_refresh_token()
    token_hash = hash_refresh_token(raw_token)

    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS),
    )
    db.add(record)
    db.commit()

    return raw_token


def get_user_from_refresh_token(db: Session, raw_token: str) -> User | None:
    if not raw_token:
        return None

    token_hash = hash_refresh_token(raw_token)
    record = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
    ).first()

    if not record or record.expires_at < datetime.utcnow():
        return None

    return db.query(User).filter(User.id == record.user_id).first()


def revoke_refresh_token(db: Session, raw_token: str):
    if not raw_token:
        return

    token_hash = hash_refresh_token(raw_token)
    db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).update({"revoked": True})
    db.commit()
