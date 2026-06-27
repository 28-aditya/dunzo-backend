from sqlalchemy.orm import Session
from db.models import Task, Note, UserSettings, Category, LinkedTasks
import uuid


def get_tasks(db: Session, user_id: str):
    user_id = uuid.UUID(str(user_id))
    return db.query(Task).filter(Task.user_id == user_id).all()


def get_notes(db: Session, user_id: str):
    user_id = uuid.UUID(str(user_id))
    return db.query(Note).filter(Note.user_id == user_id).all()


def get_settings(db: Session, user_id: str):
    user_id = uuid.UUID(str(user_id))

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings

def get_categories(db: Session, user_id: str):
    user_id = uuid.UUID(str(user_id))
    return db.query(Category).filter(Category.user_id == user_id).all()

def get_linked_tasks(db, user_id):
    return db.query(LinkedTasks).join(Note).filter(Note.user_id == user_id).all()