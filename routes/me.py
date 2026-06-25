from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from services.data_service import get_notes, get_tasks, get_settings, get_categories
from utils.helpers import to_dict
from db.models import User
from schemas.user import UserStateUpdate
from services import user_service

router = APIRouter()

@router.get("/api/me")
def get_me(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        },
        "tasks": [to_dict(t) for t in get_tasks(db, user.id)],
        "notes": [to_dict(n) for n in get_notes(db, user.id)],
        "added_categories": [to_dict(c) for c in get_categories(db, user.id)],
        "settings": to_dict(get_settings(db, user.id))
    }

