import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)

    auth_provider = Column(String)
    provider_user_id = Column(String, nullable=True, index=True)

    password_hash = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())