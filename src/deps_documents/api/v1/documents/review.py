from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body
from fastapi.params import Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.document.reviewer import ReviewerModel
from deps_documents.api.models.strict_str import StrictStr
from deps_documents.api.v1.serializers.review_document import SerializedDocumentId
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(route_class=MarkerRoute)


@router.post("/complete", response_model=DocumentModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def complete_review(
    document_id: str = Body(..., alias="documentId", embed=True, min_length=1),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return DocumentModel.from_domain(document_service.complete_review(document_entity_pk=DocumentEntityPk(document_id)))


@router.post("/start-review", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def start_review(
    document_ids: SerializedDocumentId,
    reassign_reviewer: bool = Depends(Provide[Container.config.reviewer_reassign_enabled]),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return [
        DocumentModel.from_domain(doc_entity)
        for doc_entity in document_service.start_review(
            document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in document_ids.document_ids],
            reviewer=ReviewerModel.from_current_user(),
            reassign_reviewer=reassign_reviewer,
        )
    ]


@router.post("/reset-reviewer", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def reset_reviewer(
    document_ids: list[StrictStr] = Body(..., alias="documentIds", min_length=1, embed=True),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return [
        DocumentModel.from_domain(doc_entity)
        for doc_entity in document_service.reset_reviewer([DocumentEntityPk(doc_id) for doc_id in document_ids])
    ]
