from sqlalchemy import select, Column, String, Integer, DateTime, Date
from sqlalchemy.orm import sessionmaker, Session
from db.models import User
from passlib.context import CryptContext
from datetime import datetime, timezone
from dotenv import load_dotenv
from db.session import Base, engine, SessionLocal
from fastapi import Request, HTTPException
from core.security import verify_token

import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_or_get_user(userDict, db: Session):

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

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload