from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from schemas.note import NoteCreate, NoteUpdate
from services import note_service

router = APIRouter(prefix="/api/notes")

@router.post("")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return note_service.create_note(db, user.id, note)


@router.put("/{note_id}")
def update_note(
    note_id: int,
    note: NoteUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return note_service.update_note(db, user.id, note_id, note)


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return note_service.delete_note(db, user.id, note_id)