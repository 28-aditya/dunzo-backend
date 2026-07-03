from sqlalchemy.orm import Session
from db.models import Category
from schemas.category import CategoryCreate
from utils.helpers import to_uuid


def create_category(db: Session, user_id, category: CategoryCreate):
    user_uuid = to_uuid(user_id)
    name = category.name.strip()

    existing = db.query(Category).filter(
        Category.user_id == user_uuid,
        Category.name == name
    ).first()

    if existing:
        return existing

    new_category = Category(user_id=user_uuid, name=name)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category
