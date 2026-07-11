from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from services.data_service import (
    get_notes,
    get_tasks,
    get_settings,
    get_categories,
    get_linked_tasks
)
from utils.helpers import to_dict
from db.models import User
from services import user_service
from services import task_service
from schemas.user import UserStateUpdate, UserProfileUpdate
from fastapi import HTTPException

router = APIRouter()


@router.get("/api/me")
def get_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task_service.auto_archive_completed_tasks(db, user.id)

    notes = get_notes(db, user.id)
    tasks = get_tasks(db, user.id)

    linked_tasks = get_linked_tasks(db, user.id)

    # group links by note_id
    note_links = {}

    for link in linked_tasks:
        nid = str(link.note_id)

        if nid not in note_links:
            note_links[nid] = []

        note_links[nid].append({
            "task_id": str(link.task_id),
            "title": link.task.title
        })

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        },
        "tasks": [to_dict(t) for t in tasks],
        "notes": [
            {
                **to_dict(n),
                "linked_tasks": note_links.get(str(n.id), [])
            }
            for n in notes
        ],
        "added_categories": [to_dict(c) for c in get_categories(db, user.id)],
        "settings": to_dict(get_settings(db, user.id))
    }


@router.put("/user/state")
def update_user_state(
    state: UserStateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return user_service.update_user_state(
        state,
        user.id,
        db
    )

@router.put("/api/me/profile")
def update_profile(
    body: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != user.id).first()
        if existing:
            raise HTTPException(400, "Email already in use")
        user.email = body.email
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "email": user.email, "name": user.name}