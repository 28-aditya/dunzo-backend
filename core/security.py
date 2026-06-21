import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

def create_token(payload):
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_token(token):
    return