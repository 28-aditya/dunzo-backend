from fastapi import FastAPI
from auth.google import router as google_router


app = FastAPI()

app.include_router(google_router)
