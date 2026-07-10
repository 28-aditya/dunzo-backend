import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base
from utils.helpers import utc_now


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)
    name  = Column(String, nullable=False)

    auth_provider    = Column(String)
    provider_user_id = Column(String, nullable=True, index=True)

    password_hash = Column(String, nullable=True)
    is_verified   = Column(Boolean, default=False, nullable=False)

    created_at   = Column(DateTime, server_default=func.now())
    current_view = Column(String, default="dashboard", nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title       = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category    = Column(String, nullable=True)
    status      = Column(String, nullable=False)

    due_date = Column(String, nullable=True)
    due_time = Column(String, nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    completed_at = Column(DateTime, nullable=True)

    is_archived = Column(Boolean, default=False)

    linked_tasks = relationship("LinkedTasks", back_populates="task")


class Note(Base):
    __tablename__ = "notes"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title   = Column(String, nullable=True)
    content = Column(String, nullable=False)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime)

    linked_tasks = relationship("LinkedTasks", back_populates="note",
                                cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name       = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    dark_theme     = Column(Boolean, default=True)
    daily_goal     = Column(Integer, default=1)
    auto_archive   = Column(Boolean, default=False)
    notify_overdue = Column(Boolean, default=True)


class Notification(Base):
    __tablename__ = "notifications"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    type    = Column(String)
    message = Column(String)

    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)


class LinkedTasks(Base):
    __tablename__ = "linked_tasks"
    __table_args__ = (
        UniqueConstraint("note_id", "task_id", name="uq_linked_tasks_note_task"),
    )

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=utc_now)

    note = relationship("Note", back_populates="linked_tasks")
    task = relationship("Task", back_populates="linked_tasks")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    token_hash = Column(String, nullable=False, unique=True, index=True)

    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False, nullable=False)