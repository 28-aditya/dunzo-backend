from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/notes")

@router.post("")
def create_note():
    pass

@router.put("/{note_id}")
def update_note():
    pass

@router.delete("/{note_id}")
def delete_note():
    pass