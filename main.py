from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from auth.google     import router as google_router
from auth.email_auth import router as email_router
from auth.session    import router as session_router
from db.session      import Base, engine
from routes          import me, notes, tasks, settings, linked_task, categories

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("APP_BASE_URL"),
                   os.getenv("SECONDARY_CORS_ORIGIN"),
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google_router)
app.include_router(email_router)
app.include_router(session_router)
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(settings.router)
app.include_router(me.router)
app.include_router(linked_task.router)
app.include_router(categories.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)