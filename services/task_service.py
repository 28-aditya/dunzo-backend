from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Task, LinkedTasks
from schemas.task import TaskCreate, TaskUpdate
from datetime import datetime
import uuid


def create_task(db: Session, user_id: str, task: TaskCreate):
    new_task = Task(
        user_id=uuid.UUID(user_id),
        title=task.title,
        description=task.description,
        category=task.category,
        due_date=task.due_date,
        due_time=task.due_time,
        status=task.status,
        is_archived=False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def update_task(db: Session, user_id: str, task_id: str, task: TaskUpdate):
    existing = db.query(Task).filter(
        Task.id == uuid.UUID(task_id),
        Task.user_id == uuid.UUID(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    # safe partial updates
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
        existing.status = task.status

    if task.is_archived is not None:
        existing.is_archived = task.is_archived

    existing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing)
    return existing


def delete_task(db: Session, user_id: str, task_id: str):
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(user_id)

    existing = db.query(Task).filter(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    # clean up linked tasks (important for your Note ↔ Task system)
    db.query(LinkedTasks).filter(
        LinkedTasks.task_id == task_uuid
    ).delete()

    db.delete(existing)
    db.commit()

    return {"deleted": task_id}