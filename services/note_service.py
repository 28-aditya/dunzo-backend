from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Note, LinkedTasks
from schemas.note import NoteCreate, NoteUpdate
from datetime import datetime
import uuid


def create_note(db: Session, user_id, note: NoteCreate):
    new_note = Note(
        user_id=uuid.UUID(str(user_id)),
        title=note.title,
        content=note.content
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


def update_note(db: Session, user_id, note_id: str, note: NoteUpdate):
    existing = db.query(Note).filter(
        Note.id == uuid.UUID(note_id),
        Note.user_id == uuid.UUID(str(user_id))
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    # safe updates (don’t overwrite with None)
    if note.title is not None:
        existing.title = note.title

    if note.content is not None:
        existing.content = note.content

    existing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing)
    return existing


def delete_note(db: Session, user_id, note_id: str):
    note_uuid = uuid.UUID(note_id)
    user_uuid = uuid.UUID(str(user_id))

    existing = db.query(Note).filter(
        Note.id == note_uuid,
        Note.user_id == user_uuid
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    # IMPORTANT: clean up linked tasks first
    db.query(LinkedTasks).filter(
        LinkedTasks.note_id == note_uuid
    ).delete()

    db.delete(existing)
    db.commit()

    return {"deleted": note_id}