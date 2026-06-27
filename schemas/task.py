from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    due_date: Optional[str] = ""
    due_time: Optional[str] = ""
    status:str

class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    due_date: Optional[str] = ""
    due_time: Optional[str] = ""
    status: str
    is_archived: bool