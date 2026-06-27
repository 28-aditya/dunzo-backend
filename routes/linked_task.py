from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from schemas.linked_task import LinkedTaskCreate
from services import linked_task_service

router = APIRouter(prefix="/api/notes")


@router.post("/{note_id}/tasks")
def add_task_to_note(
    note_id: str,
    payload: LinkedTaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return linked_task_service.add_task_to_note(
        db,
        user.id,
        note_id,
        payload.task_id
    )


@router.delete("/{note_id}/tasks/{task_id}")
def remove_task_from_note(
    note_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return linked_task_service.remove_task_from_note(
        db,
        user.id,
        note_id,
        task_id
    )