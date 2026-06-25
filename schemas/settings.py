from pydantic import BaseModel

class SettingsUpdate(BaseModel):
    dark_theme: bool
    daily_goal: int
    auto_archive: bool
    notify_overdue: bool