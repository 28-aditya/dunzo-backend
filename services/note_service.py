from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import Note, LinkedTasks
from schemas.note import NoteCreate, NoteUpdate
from utils.helpers import to_uuid, utc_now


def create_note(db: Session, user_id, note: NoteCreate):
    new_note = Note(
        user_id=to_uuid(user_id),
        title=note.title,
        content=note.content
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


def update_note(db: Session, user_id, note_id: str, note: NoteUpdate):
    existing = db.query(Note).filter(
        Note.id == to_uuid(note_id),
        Note.user_id == to_uuid(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.title is not None:
        existing.title = note.title
    if note.content is not None:
        existing.content = note.content

    existing.updated_at = utc_now()

    db.commit()
    db.refresh(existing)
    return existing


def delete_note(db: Session, user_id, note_id: str):
    existing = db.query(Note).filter(
        Note.id == to_uuid(note_id),
        Note.user_id == to_uuid(user_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    db.query(LinkedTasks).filter(
        LinkedTasks.note_id == to_uuid(note_id)
    ).delete()

    db.delete(existing)
    db.commit()

    return {"deleted": note_id}