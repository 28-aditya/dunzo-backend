from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    
class TaskUpdate(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    is_completed: bool
    is_archived: bool