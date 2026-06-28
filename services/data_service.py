from sqlalchemy.orm import Session
from db.models import Task, Note, UserSettings, Category, LinkedTasks
from utils import to_uuid


def get_tasks(db: Session, user_id):
    return db.query(Task).filter(Task.user_id == to_uuid(user_id)).all()


def get_notes(db: Session, user_id):
    return db.query(Note).filter(Note.user_id == to_uuid(user_id)).all()


def get_settings(db: Session, user_id):
    uid = to_uuid(user_id)
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()

    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def get_categories(db: Session, user_id):
    return db.query(Category).filter(Category.user_id == to_uuid(user_id)).all()


def get_linked_tasks(db: Session, user_id):
    return db.query(LinkedTasks).join(Note).filter(Note.user_id == to_uuid(user_id)).all()