from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Task, LinkedTasks
from schemas.task import TaskCreate, TaskUpdate
from datetime import datetime
from utils.helpers import to_uuid
import uuid


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
        completed_at=datetime.utcnow() if task.status == "done" else None
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
            existing.completed_at = datetime.utcnow()
        elif task.status != "done" and existing.status == "done":
            existing.completed_at = None
        existing.status = task.status

    if task.is_archived is not None:
        existing.is_archived = task.is_archived

    existing.updated_at = datetime.utcnow()

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

    db.delete(existing)
    db.commit()

    return {"deleted": task_id}