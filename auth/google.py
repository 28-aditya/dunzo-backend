from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

from db.deps import get_db
from services.user_service import create_or_get_user
from core.security import create_token

router = APIRouter()


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/auth/google/login")
def google_login():
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}")


@router.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):

    async with httpx.AsyncClient() as client:
        print("CLIENT_ID:", os.getenv("GOOGLE_CLIENT_ID"))
        print("REDIRECT_URI:", os.getenv("GOOGLE_REDIRECT_URI"))
        token_res = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        })

    if token_res.status_code != 200:
        raise HTTPException(400, "Google token exchange failed")

    tokens = token_res.json()
    access_token = tokens.get("access_token")

    if not access_token:
        raise HTTPException(400, "Missing access token")

    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if user_res.status_code != 200:
        raise HTTPException(400, "Failed to fetch user info")

    user = user_res.json()

    email = user.get("email")
    name = user.get("name")

    if not email:
        raise HTTPException(400, "Google account has no email")

    db_user = create_or_get_user({
        "email": email,
        "name": name,
        "auth_provider": "google",
        "provider_user_id": user.get("sub")
    }, db)

    token = create_token({
        "user_id": str(db_user.id),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
    })

    response = RedirectResponse(
        url=f"{os.getenv("APP_BASE_URL")}/pages/dashboard.html"
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        domain="localhost"
    )

    return response