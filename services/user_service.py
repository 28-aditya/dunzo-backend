from sqlalchemy.orm import Session
from db.models import User, UserSettings
from schemas.user import UserStateUpdate
from datetime import datetime, timezone
import uuid
from fastapi import HTTPException


def create_or_get_user(userDict, db: Session):

    user = db.query(User).filter(User.email == userDict["email"]).first()

    if user:
        return user

    new_user = User(
        email=userDict["email"],
        name=userDict.get("name"),
        auth_provider=userDict.get("auth_provider"),
        created_at=datetime.now(timezone.utc),
        password_hash=userDict.get("password_hash"),
        provider_user_id=userDict.get("provider_user_id")
    )

    db.add(new_user)

    # create default settings row (IMPORTANT)
    db.add(
        UserSettings(
            user_id=new_user.id
        )
    )

    db.commit()
    db.refresh(new_user)

    return new_user


def update_user_state(
    current_view: UserStateUpdate,
    user_id: str,
    db: Session
):

    existing = db.query(User).filter(
        User.id == uuid.UUID(str(user_id))
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    existing.current_view = current_view.current_view

    db.commit()
    db.refresh(existing)

    return existing