from sqlalchemy.orm import Session
from db.models import User, UserSettings
from schemas.user import UserStateUpdate
from datetime import datetime, timezone
from utils import to_uuid
from fastapi import HTTPException


def create_or_get_user(userDict: dict, db: Session) -> User:
    user = db.query(User).filter(User.email == userDict["email"]).first()

    if user:
        return user

    new_user = User(
        email            = userDict["email"],
        name             = userDict.get("name") or userDict["email"].split("@")[0],
        auth_provider    = userDict.get("auth_provider"),
        created_at       = datetime.now(timezone.utc),
        password_hash    = userDict.get("password_hash"),
        provider_user_id = userDict.get("provider_user_id"),
        is_verified      = userDict.get("is_verified", False),
    )

    db.add(new_user)
    db.add(UserSettings(user_id=new_user.id))
    db.commit()
    db.refresh(new_user)

    return new_user


def update_user_state(current_view: UserStateUpdate, user_id, db: Session) -> User:
    user = db.query(User).filter(User.id == to_uuid(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.current_view = current_view.current_view
    db.commit()
    db.refresh(user)

    return user