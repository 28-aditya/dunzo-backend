from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.google import router as google_router

from db.session import Base, engine
from routes import me, notes, tasks, settings

from dotenv import load_dotenv

import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = [os.getenv("APP_BASE_URL")],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"]
)

app.include_router(google_router)

app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(settings.router)
app.include_router(me.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)