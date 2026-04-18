from fastapi import APIRouter

from .analytics import router as analytics_router
from .debug import router as debug_router
from .document_file import router as document_file_router
from .documents import router as document_router
from .documents.brief_documents_info import router as brief_documents_info_router
from .documents.list import router as document_list_router
from .labels import router as labels_router
from .relations import router as relations_router
from .statistic import router as statistic_router

router = APIRouter(prefix="/v1")
v1_router = router

router.include_router(analytics_router)
router.include_router(debug_router)
router.include_router(document_file_router)
router.include_router(document_router)
router.include_router(document_list_router)
router.include_router(relations_router)
router.include_router(labels_router)
router.include_router(statistic_router)
router.include_router(brief_documents_info_router, tags=["Brief document info"])
