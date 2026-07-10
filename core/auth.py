from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from db.deps import get_db
from db.models import User
from core.security import verify_token
from utils.helpers import to_uuid


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Bad token payload")

    user = db.query(User).filter(User.id == to_uuid(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
