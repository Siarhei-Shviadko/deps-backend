from fastapi import APIRouter

from .comments import router as comments_router
from .create import router as create_router
from .detail import router as detail_router
from .extract import router as extract_router
from .files import router as files_router
from .labels import router as labels_router
from .metadata import router as metadata_router
from .pipeline import router as pipeline_router
from .review import router as review_router
from .states import router as states_router
from .types import router as types_router
from .upload import router as upload_router
from .validation import router as validation_router

router = APIRouter(prefix="/documents", tags=["Documents"])

router.include_router(states_router)
router.include_router(comments_router, tags=["Comments"])
router.include_router(files_router, tags=["Files"])
router.include_router(labels_router, tags=["Labels"])
router.include_router(pipeline_router, tags=["Pipeline management"])
router.include_router(review_router, tags=["Review"])
router.include_router(types_router)
router.include_router(upload_router, tags=["Upload"])
router.include_router(extract_router, tags=["Extraction"])
router.include_router(detail_router)
router.include_router(validation_router, tags=["Validation"])
router.include_router(metadata_router)
router.include_router(create_router, tags=["Creation"])
