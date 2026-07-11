from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

load_dotenv()

from core.config import validate_env
validate_env()

from auth.google     import router as google_router
from auth.email_auth import router as email_router
from auth.session    import router as session_router
from db.session      import Base, engine
from routes          import me, notes, tasks, settings, linked_task, categories, notifications
from core.limiter    import limiter

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

_cors_origins = [
    os.getenv("APP_BASE_URL"),
    os.getenv("SECONDARY_CORS_ORIGIN"),
]

_cors_origins = [origin for origin in _cors_origins if origin]

print("CORS:", _cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
app.include_router(notifications.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)