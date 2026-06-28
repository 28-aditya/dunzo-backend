from pydantic import BaseModel

class LinkedTaskCreate(BaseModel):
    note_id: str
    task_id: str

class LinkedTaskDelete(BaseModel):
    note_id: str
    task_id: str