from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/settings")

@router.put("")
def update_settings():
    pass