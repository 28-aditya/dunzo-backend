import os
import resend
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
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
from schemas.email_auth import (
    ResetPasswordRequest,
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest
)

router = APIRouter(prefix="/auth/email")

resend.api_key = os.getenv("RESEND_API_KEY")

# ─────────────────────────────────────────
# Email helper
# ─────────────────────────────────────────

def _send_email(to: str, subject: str, html: str) -> None:
    resend.Emails.send({
        "from": "dunzo <onboarding@resend.dev>",
        "to": to,
        "subject": subject,
        "html": html,
    })


def _make_verify_email(name: str, link: str) -> str:
    return f"""
    <div style="background:#111;min-height:100vh;padding:48px 16px;font-family:'Inter',sans-serif">
      <div style="max-width:480px;margin:auto;background:#1a1a1a;border-radius:16px;
                  border:1px solid #2a2a2a;overflow:hidden">

        <!-- Header -->
        <div style="padding:32px 32px 24px;border-bottom:1px solid #2a2a2a">
          <h1 style="margin:0;font-size:24px;color:#c8f261;letter-spacing:-0.5px">dunzo.</h1>
        </div>

        <!-- Body -->
        <div style="padding:32px">
          <h2 style="margin:0 0 8px;font-size:20px;color:#f5f5f5;font-weight:600">
            Verify your email
          </h2>
          <p style="margin:0 0 24px;color:#888;font-size:14px;line-height:1.6">
            Hey {name}, welcome to dunzo. Click the button below to verify your email
            address and activate your account.
          </p>

          <a href="{link}"
             style="display:inline-block;background:#c8f261;color:#111;
                    padding:14px 32px;border-radius:10px;text-decoration:none;
                    font-weight:700;font-size:15px;letter-spacing:-0.2px">
            Verify email →
          </a>

          <p style="margin:24px 0 0;color:#555;font-size:12px;line-height:1.6">
            This link expires in 24 hours. If you didn't create a dunzo account, you can safely ignore this email.
          </p>
        </div>

        <!-- Footer -->
        <div style="padding:20px 32px;border-top:1px solid #2a2a2a">
          <p style="margin:0;color:#444;font-size:12px">
            © 2025 dunzo. All rights reserved.
          </p>
        </div>

      </div>
    </div>"""


def _make_reset_email(name: str, link: str) -> str:
    return f"""
    <div style="background:#111;min-height:100vh;padding:48px 16px;font-family:'Inter',sans-serif">
      <div style="max-width:480px;margin:auto;background:#1a1a1a;border-radius:16px;
                  border:1px solid #2a2a2a;overflow:hidden">

        <!-- Header -->
        <div style="padding:32px 32px 24px;border-bottom:1px solid #2a2a2a">
          <h1 style="margin:0;font-size:24px;color:#c8f261;letter-spacing:-0.5px">dunzo.</h1>
        </div>

        <!-- Body -->
        <div style="padding:32px">
          <h2 style="margin:0 0 8px;font-size:20px;color:#f5f5f5;font-weight:600">
            Reset your password
          </h2>
          <p style="margin:0 0 24px;color:#888;font-size:14px;line-height:1.6">
            Hey {name}, we received a request to reset your dunzo password.
            Click the button below to choose a new one.
          </p>

          <a href="{link}"
             style="display:inline-block;background:#c8f261;color:#111;
                    padding:14px 32px;border-radius:10px;text-decoration:none;
                    font-weight:700;font-size:15px;letter-spacing:-0.2px">
            Reset password →
          </a>

          <p style="margin:24px 0 0;color:#555;font-size:12px;line-height:1.6">
            This link expires in 1 hour. If you didn't request a password reset,
            you can safely ignore this email — your password won't change.
          </p>
        </div>

        <!-- Footer -->
        <div style="padding:20px 32px;border-top:1px solid #2a2a2a">
          <p style="margin:0;color:#444;font-size:12px">
            © 2025 dunzo. All rights reserved.
          </p>
        </div>

      </div>
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

    verify_jwt = create_token({
        "purpose":  "email_verify",
        "email":    body.email,
        "name":     body.name,
        "pw_hash":  hash_password(body.password),
        "token":    verify_token_str,
        "exp":      int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
    })

    base_url = os.getenv("APP_BASE_URL")
    link     = f"http://127.0.0.1:8000/auth/email/verify?token={verify_jwt}"

    try:
        _send_email(
            to      = body.email,
            subject = "Verify your dunzo account",
            html    = _make_verify_email(body.name, link)
        )
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

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

    existing = db.query(User).filter(User.email == email).first()
    if existing:
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