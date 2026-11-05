from fastapi import APIRouter, Request
from .store import get

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}

# TODO: GET /documents/{document_id}
