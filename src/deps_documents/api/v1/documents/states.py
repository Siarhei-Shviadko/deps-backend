from fastapi import APIRouter

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.domain.constants import DocumentStateEnum

router = APIRouter(prefix="/states", tags=["States"], route_class=MarkerRoute)

_DOCUMENT_STATES = {  # noqa: WPS407
    DocumentStateEnum.PREPROCESSING: "Preprocessing",
    DocumentStateEnum.IDENTIFICATION: "Identification",
    DocumentStateEnum.VERSION_IDENTIFICATION: "Version Identification",
    DocumentStateEnum.NEW: "New",
    DocumentStateEnum.IN_REVIEW: "In Review",
    DocumentStateEnum.FAILED: "Failed",
    DocumentStateEnum.COMPLETED: "Completed",
    DocumentStateEnum.DATA_EXTRACTION: "Data Extraction",
    DocumentStateEnum.VALIDATION: "Validation",
    DocumentStateEnum.UNIFICATION: "Unification",
    DocumentStateEnum.IMAGE_PREPROCESSING: "Image Preprocessing",
    DocumentStateEnum.PARSING: "Parsing",
    DocumentStateEnum.POSTPROCESSING: "Postprocessing",
    DocumentStateEnum.NEEDS_REVIEW: "Needs Review",
    DocumentStateEnum.EXPORTING: "Exporting",
    DocumentStateEnum.EXPORTED: "Exported",
    DocumentStateEnum.EXCEPTIONAL_QUEUE: "Exceptional Queue",
    DocumentStateEnum.POSTPONED: "Postponed",
}


@router.get("", openapi_extra={"visibility": Visibility.PUBLIC})
def get_document_states():
    document_states = {}
    for key in _DOCUMENT_STATES.keys():
        document_states[key] = {
            "title": _DOCUMENT_STATES[key],
            "name": key,
        }
    return document_states
