import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    auth_provider = Column(String)
    provider_user_id = Column(String, nullable=True, index=True)

    password_hash = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    current_view = Column(String, default="dashboard", nullable=False)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)

    due_date = Column(String, nullable=True)       
    due_time = Column(String, nullable=True)       

    created_at = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)

    is_archived = Column(Boolean, default=False)

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=True)
    content = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    dark_theme = Column(Boolean, default=True)
    daily_goal = Column(Integer, default=1)
    auto_archive = Column(Boolean, default=False)
    notify_overdue = Column(Boolean, default=True)