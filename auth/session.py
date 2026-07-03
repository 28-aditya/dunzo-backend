from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.deps import get_db
from core.security import create_access_token
from services.auth_service import get_user_from_refresh_token, revoke_refresh_token

router = APIRouter(prefix="/auth")


@router.post("/refresh")
def refresh(request: Request, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get("refresh_token")
    user = get_user_from_refresh_token(db, raw_refresh)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_access_token(user.id)

    response = JSONResponse({"message": "Refreshed"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        domain="localhost",
        max_age=1800,
    )
    return response


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get("refresh_token")
    revoke_refresh_token(db, raw_refresh)

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("access_token", domain="localhost")
    response.delete_cookie("refresh_token", domain="localhost")
    return response