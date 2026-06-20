from sqlalchemy import Column, String, DateTime
from db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)

    auth_provider = Column(String)  
    provider_user_id = Column(String, nullable=True)

    password_hash = Column(String, nullable=True)

    created_at = Column(DateTime)