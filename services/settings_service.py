from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import UserSettings
from schemas.settings import SettingsUpdate
from utils import to_uuid


def update_settings(db: Session, user_id, settings: SettingsUpdate):
    existing = db.query(UserSettings).filter(
        UserSettings.user_id == to_uuid(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Settings not found")

    if settings.dark_theme is not None:
        existing.dark_theme = settings.dark_theme
    if settings.daily_goal is not None:
        existing.daily_goal = settings.daily_goal
    if settings.auto_archive is not None:
        existing.auto_archive = settings.auto_archive
    if settings.notify_overdue is not None:
        existing.notify_overdue = settings.notify_overdue

    db.commit()
    db.refresh(existing)

    return existing