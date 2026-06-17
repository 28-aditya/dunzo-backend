from fastapi import FastAPI
from auth.google import router as google_router
from auth.github import router as github_router

app = FastAPI()

app.include_router(google_router)
app.include_router(github_router)