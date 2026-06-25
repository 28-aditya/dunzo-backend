from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from schemas.task import TaskCreate, TaskUpdate
from services import task_service

router = APIRouter(prefix="/api/tasks")

@router.post("")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return task_service.create_task(db, user.id, task)


@router.put("/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return task_service.update_task(db, user.id, task_id, task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return task_service.delete_task(db, user.id, task_id)