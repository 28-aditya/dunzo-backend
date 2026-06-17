from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/google/login")

def google_login():
    return {"msg": "redirect to google"}