import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.config import COOKIE_KWARGS, RATE_LIMIT_AUTH
from core.limiter import limiter
from core.security import (
    create_access_token,
    hash_password,
    verify_password,
    is_legacy_password_hash,
    verify_password_legacy_sha256,
)
from db.deps import get_db
from db.models import User, UserSettings
from schemas.email_auth import RegisterRequest, LoginRequest
from services.auth_service import issue_refresh_token, REFRESH_TOKEN_TTL_DAYS

router = APIRouter(prefix="/auth/email")


@router.post("/register")
@limiter.limit(RATE_LIMIT_AUTH)
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    user_id = uuid.uuid4()
    db_user = User(
        id=user_id,
        email=body.email,
        name=body.name,
        auth_provider="email",
        password_hash=hash_password(body.password),
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(db_user)
    db.add(UserSettings(user_id=user_id))
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(db_user.id)
    refresh_token = issue_refresh_token(db, db_user.id)

    response = JSONResponse({"message": "Account created."})
    response.set_cookie(
        key="access_token", value=access_token, max_age=1800, **COOKIE_KWARGS
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_TTL_DAYS * 86400,
        **COOKIE_KWARGS,
    )
    return response


@router.post("/login")
@limiter.limit(RATE_LIMIT_AUTH)
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not user.password_hash:
        raise HTTPException(401, "Invalid email or password")

    if is_legacy_password_hash(user.password_hash):
        # Pre-bcrypt account. Verify against the old SHA-256 scheme, then
        # transparently upgrade to bcrypt now that we have the plaintext.
        if not verify_password_legacy_sha256(body.password, user.password_hash):
            raise HTTPException(401, "Invalid email or password")
        user.password_hash = hash_password(body.password)
        db.commit()
    else:
        if not verify_password(body.password, user.password_hash):
            raise HTTPException(401, "Invalid email or password")

    max_days = REFRESH_TOKEN_TTL_DAYS if body.remember else 1
    access_token = create_access_token(user.id)
    refresh_token = issue_refresh_token(db, user.id, expires_days=max_days)

    response = JSONResponse({"message": "Logged in"})
    response.set_cookie(
        key="access_token", value=access_token, max_age=1800, **COOKIE_KWARGS
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=max_days * 86400,
        **COOKIE_KWARGS,
    )
    return response