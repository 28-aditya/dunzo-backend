import os
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from db.deps import get_db
from db.models import User, UserSettings
from core.security import (
    create_token,
    hash_password,
    verify_password,
)
from schemas.email_auth import (
    RegisterRequest,
    LoginRequest
)

router = APIRouter(prefix="/auth/email")


# ─────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────

@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    db_user = User(
        email         = body.email,
        name          = body.name,
        auth_provider = "email",
        password_hash = hash_password(body.password),
        is_verified   = True,
        created_at    = datetime.now(timezone.utc),
    )
    db.add(db_user)
    db.add(UserSettings(user_id=db_user.id))
    db.commit()
    db.refresh(db_user)

    return {"message": "Account created. You can now sign in."}


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not user.password_hash:
        raise HTTPException(401, "Invalid email or password")

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    access_token = create_token({
        "user_id": str(user.id),
        "exp":     int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
    })

    response = JSONResponse({"message": "Logged in"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        domain="localhost",
        max_age=86400,
    )
    return response