from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models import LinkedTasks, Note, Task
from utils.helpers import to_uuid


def add_task_to_note(db: Session, user_id, note_id: str, task_id: str):
    note_uuid = to_uuid(note_id)
    task_uuid = to_uuid(task_id)
    user_uuid = to_uuid(user_id)

    note = db.query(Note).filter(
        Note.id == note_uuid,
        Note.user_id == user_uuid
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    task = db.query(Task).filter(
        Task.id == task_uuid,
        Task.user_id == user_uuid
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    existing_link = db.query(LinkedTasks).filter(
        LinkedTasks.note_id == note_uuid,
        LinkedTasks.task_id == task_uuid
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="Task already linked")

    count = db.query(LinkedTasks).filter(
        LinkedTasks.note_id == note_uuid
    ).count()

    if count >= 4:
        raise HTTPException(status_code=400, detail="Max 4 tasks per note reached")

    link = LinkedTasks(note_id=note_uuid, task_id=task_uuid)

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


def remove_task_from_note(db: Session, user_id, note_id: str, task_id: str):
    link = db.query(LinkedTasks).join(Note).filter(
        LinkedTasks.note_id == to_uuid(note_id),
        LinkedTasks.task_id == to_uuid(task_id),
        Note.user_id == to_uuid(user_id)
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(link)
    db.commit()

    return {"deleted": True}