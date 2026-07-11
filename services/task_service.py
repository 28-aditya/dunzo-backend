from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Task, LinkedTasks, Notification, UserSettings
from schemas.task import TaskCreate, TaskUpdate
from utils.helpers import to_uuid, utc_now

AUTO_ARCHIVE_AFTER_DAYS = 5


def create_task(db: Session, user_id, task: TaskCreate):
    new_task = Task(
        user_id=to_uuid(user_id),
        title=task.title,
        description=task.description,
        category=task.category,
        due_date=task.due_date,
        due_time=task.due_time,
        status=task.status,
        is_archived=False,
        completed_at=utc_now() if task.status == "done" else None
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def update_task(db: Session, user_id, task_id: str, task: TaskUpdate):
    existing = db.query(Task).filter(
        Task.id == to_uuid(task_id),
        Task.user_id == to_uuid(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.title is not None:
        existing.title = task.title
    if task.description is not None:
        existing.description = task.description
    if task.category is not None:
        existing.category = task.category
    if task.due_date is not None:
        existing.due_date = task.due_date
    if task.due_time is not None:
        existing.due_time = task.due_time

    if task.status is not None:
        # Only stamp/clear completed_at on an actual status transition,
        # so editing an already-done task doesn't reset "time since
        # last completion".
        if task.status == "done" and existing.status != "done":
            existing.completed_at = utc_now()
        elif task.status != "done" and existing.status == "done":
            existing.completed_at = None
        existing.status = task.status

    if task.is_archived is not None:
        existing.is_archived = task.is_archived

    existing.updated_at = utc_now()

    db.commit()
    db.refresh(existing)
    return existing


def delete_task(db: Session, user_id, task_id: str):
    existing = db.query(Task).filter(
        Task.id == to_uuid(task_id),
        Task.user_id == to_uuid(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    db.query(LinkedTasks).filter(
        LinkedTasks.task_id == to_uuid(task_id)
    ).delete()

    db.query(Notification).filter(
        Notification.task_id == to_uuid(task_id)
    ).delete()

    db.delete(existing)
    db.commit()

    return {"deleted": task_id}


def auto_archive_completed_tasks(db: Session, user_id):
    """Archive tasks that were marked done more than AUTO_ARCHIVE_AFTER_DAYS
    days ago. Runs on every /api/me read (no scheduler in this app), and
    only does anything when the user has the "Auto-Archive Completed"
    setting turned on.
    """
    uid = to_uuid(user_id)

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == uid
    ).first()

    if not settings or not settings.auto_archive:
        return

    cutoff = utc_now() - timedelta(days=AUTO_ARCHIVE_AFTER_DAYS)

    db.query(Task).filter(
        Task.user_id == uid,
        Task.status == "done",
        Task.is_archived == False,
        Task.completed_at.isnot(None),
        Task.completed_at <= cutoff
    ).update({"is_archived": True}, synchronize_session=False)

    db.commit()