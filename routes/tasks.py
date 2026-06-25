from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from core.auth import get_current_user
from services.data_service import get_tasks
from utils.helpers import to_dict

router = APIRouter(prefix="/api/tasks")

@router.post("")
def create_task():
    pass  

@router.put("/{task_id}")
def update_task():
    pass

@router.delete("/{task_id}")
def delete_task():
    pass