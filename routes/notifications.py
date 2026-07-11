from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from services import notification_service
from utils.helpers import to_dict

router = APIRouter(prefix="/api/notifications")


@router.get("/")
def list_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    notifs = notification_service.get_notifications(db, user.id)
    return [to_dict(n) for n in notifs]


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return {"count": notification_service.get_unread_count(db, user.id)}


@router.put("/read-all")
def read_all(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return notification_service.mark_all_read(db, user.id)


@router.put("/{notification_id}/read")
def read_one(
    notification_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return to_dict(notification_service.mark_read(db, user.id, notification_id))


@router.delete("/{notification_id}")
def delete_one(
    notification_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return notification_service.delete_notification(db, user.id, notification_id)