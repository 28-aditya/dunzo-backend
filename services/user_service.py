from sqlalchemy import select, Column, String, Integer, DateTime, Date
from sqlalchemy.orm import sessionmaker
from db.models import User
from passlib.context import CryptContext
from datetime import datetime, timezone
from dotenv import load_dotenv
from db.session import Base, engine, SessionLocal

import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_or_get_user(userDict):

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == userDict["email"]).first()
        
        if user:
            return user
        
        new_user = User(
            email=userDict["email"],
            name=userDict.get("name"),
            auth_provider=userDict.get("auth_provider"),
            created_at = datetime.now(timezone.utc),
            password_hash = userDict.get("password_hash"),
            provider_user_id = userDict.get("provider_user_id")
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    finally:
        db.close()