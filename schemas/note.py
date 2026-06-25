from pydantic import BaseModel
from typing import Optional

class NoteCreate(BaseModel):
    title: Optional[str] = ""
    content: str

class NoteUpdate(BaseModel):
    id: int
    title: Optional[str] = ""
    content: str