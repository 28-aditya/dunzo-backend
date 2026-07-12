from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Notification, Task
from utils.helpers import to_uuid, utc_now

DUE_SOON_WINDOW_MINUTES = 30


def _parse_due_datetime(task: Task):
    """Combine a task's due_date/due_time strings into a naive datetime.

    due_date/due_time are plain strings coming from <input type="date"> and
    <input type="time"> with no timezone info attached anywhere in the app
    (frontend and backend both already compare naive local timestamps
    directly, e.g. `new Date(`${date}T${time}`)` on the client). This mirrors
    that existing assumption rather than introducing a new one.
    """
    if not task.due_date or not task.due_time:
        return None
    try:
        return datetime.strptime(f"{task.due_date} {task.due_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def _ensure_notification(db: Session, uid, task: Task, type_: str, message: str):
    existing = db.query(Notification).filter(
        Notification.user_id == uid,
        Notification.task_id == task.id,
        Notification.type == type_
    ).first()

    if existing:
        return existing

    notif = Notification(
        user_id=uid,
        task_id=task.id,
        type=type_,
        message=message,
        is_read=False
    )
    db.add(notif)
    db.flush()
    return notif


def sync_notifications(db: Session, user_id) -> None:
    """Create overdue / due-soon notifications for active tasks and clean up
    ones that no longer apply (task completed, rescheduled, archived, or
    deleted). Called on every notification read so no separate scheduler is
    needed.
    """
    uid = to_uuid(user_id)
    now = utc_now()

    tasks = db.query(Task).filter(
        Task.user_id == uid,
        Task.is_archived.isnot(True)
    ).all()

    still_valid = set()

    for task in tasks:
        if task.status == "done":
            continue

        due_dt = _parse_due_datetime(task)
        if not due_dt:
            continue

        if due_dt < now:
            still_valid.add((task.id, "overdue"))
            _ensure_notification(db, uid, task, "overdue",
                                  f'"{task.title}" is overdue')
        elif (due_dt - now) <= timedelta(minutes=DUE_SOON_WINDOW_MINUTES):
            still_valid.add((task.id, "due_soon"))
            _ensure_notification(db, uid, task, "due_soon",
                                  f'"{task.title}" is due in 30 minutes')

    stale = db.query(Notification).filter(
        Notification.user_id == uid,
        Notification.type.in_(["overdue", "due_soon"])
    ).all()

    for notif in stale:
        if (notif.task_id, notif.type) not in still_valid:
            db.delete(notif)

    db.commit()


def get_notifications(db: Session, user_id):
    sync_notifications(db, user_id)
    return db.query(Notification).filter(
        Notification.user_id == to_uuid(user_id)
    ).order_by(Notification.created_at.desc()).all()


def get_unread_count(db: Session, user_id):
    sync_notifications(db, user_id)
    return db.query(Notification).filter(
        Notification.user_id == to_uuid(user_id),
        Notification.is_read == False
    ).count()


def mark_read(db: Session, user_id, notification_id: str):
    notif = db.query(Notification).filter(
        Notification.id == to_uuid(notification_id),
        Notification.user_id == to_uuid(user_id)
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_read(db: Session, user_id):
    db.query(Notification).filter(
        Notification.user_id == to_uuid(user_id),
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"marked_read": True}


def delete_notification(db: Session, user_id, notification_id: str):
    notif = db.query(Notification).filter(
        Notification.id == to_uuid(notification_id),
        Notification.user_id == to_uuid(user_id)
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notif)
    db.commit()

    return {"deleted": notification_id}