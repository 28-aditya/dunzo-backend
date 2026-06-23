from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from services.data_service import get_notes, get_tasks, get_settings

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
        "tasks": get_tasks(db, user.id),
        "notes": get_notes(db, user.id),
        "settings": get_settings(db, user.id)
    }