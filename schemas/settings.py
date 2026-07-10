from pydantic import BaseModel
from typing import Optional


class SettingsUpdate(BaseModel):
    dark_theme: Optional[bool] = None
    daily_goal: Optional[int] = None
    auto_archive: Optional[bool] = None
    notify_overdue: Optional[bool] = None
