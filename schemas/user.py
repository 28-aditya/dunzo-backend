from pydantic import BaseModel

class UserStateUpdate(BaseModel):
    current_view: str