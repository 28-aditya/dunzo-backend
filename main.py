from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
load_dotenv()
print("CORS origin:", os.getenv("APP_BASE_URL"))  # add this temporarily
from auth.google     import router as google_router
from auth.email_auth import router as email_router
from db.session      import Base, engine
from routes          import me, notes, tasks, settings, linked_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("APP_BASE_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google_router)
app.include_router(email_router)
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(settings.router)
app.include_router(me.router)
app.include_router(linked_task.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)