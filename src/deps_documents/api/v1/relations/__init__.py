from fastapi import APIRouter

from .assign import router as assign_router
from .children import router as children_router
from .detail import router as detail_router
from .documents import router as document_router
from .list import router as list_router
from .type_list import router as type_list_router

router = APIRouter(prefix="/relations", tags=["Relations"])

router.include_router(list_router)
router.include_router(assign_router)
router.include_router(children_router)
router.include_router(document_router)
router.include_router(type_list_router)
router.include_router(detail_router)
