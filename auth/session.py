from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.config import COOKIE_KWARGS, RATE_LIMIT_REFRESH
from core.limiter import limiter
from core.security import create_access_token
from db.deps import get_db
from services.auth_service import rotate_refresh_token, revoke_refresh_token

router = APIRouter(prefix="/auth")


@router.post("/refresh")
@limiter.limit(RATE_LIMIT_REFRESH)
def refresh(request: Request, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get("refresh_token")
    result = rotate_refresh_token(db, raw_refresh)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user, new_refresh, remaining_days = result
    access_token = create_access_token(user.id)

    response = JSONResponse({"message": "Refreshed"})
    response.set_cookie(
        key="access_token", value=access_token, max_age=1800, **COOKIE_KWARGS
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        max_age=remaining_days * 86400,
        **COOKIE_KWARGS,
    )
    return response


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get("refresh_token")
    revoke_refresh_token(db, raw_refresh)

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("access_token", **COOKIE_KWARGS)
    response.delete_cookie("refresh_token", **COOKIE_KWARGS)
    return response
