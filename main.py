from fastapi import FastAPI

from auth.google import router as google_router

from db.session import Base, engine
from routes.me import router as me_router

app = FastAPI()

app.include_router(google_router)
app.include_router(me_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)