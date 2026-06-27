from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import LinkedTasks, Note, Task
import uuid


def add_task_to_note(db: Session, user_id: str, note_id: str, task_id: str):

    note_uuid = uuid.UUID(note_id)
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(str(user_id))

    # verify note belongs to user
    note = db.query(Note).filter(
        Note.id == note_uuid,
        Note.user_id == user_uuid
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # verify task belongs to user
    task = db.query(Task).filter(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # prevent duplicates
    existing_link = db.query(LinkedTasks).filter(
        LinkedTasks.note_id == note_uuid,
        LinkedTasks.task_id == task_uuid
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="Task already linked")

    # enforce max 4 tasks per note
    count = db.query(LinkedTasks).filter(
        LinkedTasks.note_id == note_uuid
    ).count()

    if count >= 4:
        raise HTTPException(status_code=400, detail="Max 4 tasks per note reached")

    link = LinkedTasks(
        note_id=note_uuid,
        task_id=task_uuid
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


def remove_task_from_note(db: Session, user_id: str, note_id: str, task_id: str):

    note_uuid = uuid.UUID(note_id)
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(str(user_id))

    link = db.query(LinkedTasks).join(Note).filter(
        LinkedTasks.note_id == note_uuid,
        LinkedTasks.task_id == task_uuid,
        Note.user_id == user_uuid
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(link)
    db.commit()

    return {"deleted": True}