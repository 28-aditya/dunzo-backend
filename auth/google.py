from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from services.user_service import create_or_get_user
from datetime import timedelta, timezone, datetime
from core.security import create_token, verify_token

import os
import httpx

router = APIRouter()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

@router.get("/auth/google/login")

def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline"
    }

    from urllib.parse import urlencode
    query = urlencode(params)
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/auth/google/callback")
async def google_callback(code: str):
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_res = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })

    tokens = token_res.json()
    access_token = tokens.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    # Fetch user info from Google
    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    user = user_res.json()

    # `user` now has: email, name, picture, sub (Google's user ID)
    # Next step: save to DB and return a JWT — placeholder for now
    userDict= {
        "email": user.get("email"),
        "name": user.get("name"),
        "auth_provider": "google",
        "provider_user_id": user.get("sub")
    }

    db_user = create_or_get_user(userDict)

    jwt_payload = {
        "user_id":db_user.id,
        "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
    }

    current_session_token = create_token(jwt_payload)

    return {
        "access_token": current_session_token,
        "token_type": "bearer"
    }
