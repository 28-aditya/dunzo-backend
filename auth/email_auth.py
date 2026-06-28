"""
Email sign-up / sign-in / verify / forgot-password routes.

Requires these env vars:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS   — outgoing email
  APP_BASE_URL                                  — e.g. http://localhost:5500
  JWT_SECRET, PASSWORD_SALT                     — already used elsewhere
"""

import os
import smtplib
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from db.deps import get_db
from db.models import User, UserSettings
from core.security import (
    create_token,
    verify_token,
    hash_password,
    verify_password,
    generate_verification_token,
)

router = APIRouter(prefix="/auth/email")


# ─────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token:    str
    password: str


# ─────────────────────────────────────────
# Email helper
# ─────────────────────────────────────────

def _send_email(to: str, subject: str, html: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_user, smtp_pass]):
        # In local dev without SMTP configured, just print the link
        print(f"[EMAIL] To: {to} | Subject: {subject}")
        print(f"[EMAIL] Body: {html}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = to
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to, msg.as_string())


def _make_verify_email(name: str, link: str) -> str:
    return f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#c8f261">dunzo.</h2>
      <p>Hi {name},</p>
      <p>Click the button below to verify your email address.</p>
      <a href="{link}" style="display:inline-block;background:#c8f261;color:#111;
         padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600">
        Verify email
      </a>
      <p style="color:#888;font-size:12px;margin-top:24px">
        This link expires in 24 hours. If you didn't create an account, ignore this email.
      </p>
    </div>"""


def _make_reset_email(name: str, link: str) -> str:
    return f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#c8f261">dunzo.</h2>
      <p>Hi {name},</p>
      <p>Click the button below to reset your password.</p>
      <a href="{link}" style="display:inline-block;background:#c8f261;color:#111;
         padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600">
        Reset password
      </a>
      <p style="color:#888;font-size:12px;margin-top:24px">
        This link expires in 1 hour. If you didn't request a reset, ignore this email.
      </p>
    </div>"""


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

    verify_token_str = generate_verification_token()

    # Store the token as a short-lived JWT so we don't need a separate DB column
    verify_jwt = create_token({
        "purpose":    "email_verify",
        "email":      body.email,
        "name":       body.name,
        "pw_hash":    hash_password(body.password),
        "token":      verify_token_str,
        "exp":        int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
    })

    base_url = os.getenv("APP_BASE_URL")
    link     = f"{base_url}/pages/verify-email.html?token={verify_jwt}"

    try:
        _send_email(
            to      = body.email,
            subject = "Verify your dunzo account",
            html    = _make_verify_email(body.name, link)
        )
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        # Don't block registration if email fails in dev

    return {"message": "Check your email to verify your account."}


# ─────────────────────────────────────────
# VERIFY EMAIL
# ─────────────────────────────────────────

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)

    if not payload or payload.get("purpose") != "email_verify":
        raise HTTPException(400, "Invalid or expired verification link")

    email   = payload["email"]
    name    = payload["name"]
    pw_hash = payload["pw_hash"]

    # Check not already registered (could have clicked link twice)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        # Already verified — just log them in
        db_user = existing
    else:
        db_user = User(
            email         = email,
            name          = name,
            auth_provider = "email",
            password_hash = pw_hash,
            is_verified   = True,
            created_at    = datetime.now(timezone.utc),
        )
        db.add(db_user)
        db.add(UserSettings(user_id=db_user.id))
        db.commit()
        db.refresh(db_user)

    access_token = create_token({
        "user_id": str(db_user.id),
        "exp":     int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
    })

    base_url = os.getenv("APP_BASE_URL")
    response = RedirectResponse(url=f"{base_url}/pages/dashboard.html")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        domain="localhost",
        max_age=86400,
    )
    return response


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

    if not user.is_verified:
        raise HTTPException(403, "Please verify your email before signing in")

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


# ─────────────────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────────────────

@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    # Always return success to avoid email enumeration
    if not user or user.auth_provider != "email":
        return {"message": "If that email exists, a reset link has been sent."}

    reset_jwt = create_token({
        "purpose": "password_reset",
        "user_id": str(user.id),
        "exp":     int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    })

    base_url = os.getenv("APP_BASE_URL")
    link     = f"{base_url}/pages/reset-password.html?token={reset_jwt}"

    try:
        _send_email(
            to      = user.email,
            subject = "Reset your dunzo password",
            html    = _make_reset_email(user.name, link)
        )
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

    return {"message": "If that email exists, a reset link has been sent."}


# ─────────────────────────────────────────
# RESET PASSWORD
# ─────────────────────────────────────────

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = verify_token(body.token)

    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(400, "Invalid or expired reset link")

    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.password_hash = hash_password(body.password)
    db.commit()

    return {"message": "Password updated. You can now sign in."}