from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from schemas.category import CategoryCreate
from services import category_service

router = APIRouter(prefix="/api/categories")


@router.post("/")
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return category_service.create_category(db, user.id, category)