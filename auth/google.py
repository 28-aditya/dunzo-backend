import os
import secrets
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.config import COOKIE_KWARGS, RATE_LIMIT_AUTH
from core.limiter import limiter
from core.security import create_access_token
from db.deps import get_db
from services.auth_service import issue_refresh_token, REFRESH_TOKEN_TTL_DAYS
from services.user_service import create_or_get_user

load_dotenv()

router = APIRouter()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/auth/google/login")
@limiter.limit(RATE_LIMIT_AUTH)
def google_login(request: Request):
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    query_string = urlencode(params)
    response = RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    )
    response.set_cookie(key="oauth_state", value=state, max_age=600, **COOKIE_KWARGS)
    return response


@router.get("/auth/google/callback")
@limiter.limit(RATE_LIMIT_AUTH)
async def google_callback(
    code: str, state: str, request: Request, db: Session = Depends(get_db)
):
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or cookie_state != state:
        raise HTTPException(400, "Invalid OAuth state")

    async with httpx.AsyncClient() as client:
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
    google_access_token = tokens.get("access_token")

    if not google_access_token:
        raise HTTPException(400, "Missing access token")

    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
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
        "provider_user_id": user.get("sub"),
    }, db)

    access_token = create_access_token(db_user.id)
    refresh_token = issue_refresh_token(db, db_user.id)

    response = RedirectResponse(
        url=f"{os.getenv('APP_BASE_URL')}/pages/dashboard.html"
    )

    response.set_cookie(
        key="access_token", value=access_token, max_age=1800, **COOKIE_KWARGS
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_TTL_DAYS * 86400,
        **COOKIE_KWARGS,
    )
    response.delete_cookie("oauth_state", **COOKIE_KWARGS)

    return response
