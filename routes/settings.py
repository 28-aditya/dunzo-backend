from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from schemas.settings import SettingsUpdate
from services import settings_service

router = APIRouter(prefix="/api/settings")


@router.put("/")
def update_settings(
    settings: SettingsUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return settings_service.update_settings(db, user.id, settings)

@router.get("/")
def get_settings(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return settings_service.get_settings(db, user.id)