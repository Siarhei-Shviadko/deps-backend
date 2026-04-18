from fastapi import APIRouter

from .documents.endpoints import document_router

v2_router = APIRouter(prefix="/v2", tags=["v2"])

v2_router.include_router(document_router)
