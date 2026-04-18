from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.reviewer import ReviewerModel
from deps_documents.application import DocumentAccessServiceV2 as DocumentAccessService
from deps_documents.auth import get_current_user_organisation
from deps_documents.containers import Container

from ..serializers import CreateDocumentRequest, CreateDocumentResponse

router = APIRouter(prefix="/create-document", route_class=MarkerRoute)


@router.post("", response_model=CreateDocumentResponse, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def create_document(
    create_document_request: CreateDocumentRequest,
    document_access_service: DocumentAccessService = Depends(Provide[Container.application.document_access]),
):
    document_id = document_access_service.create_document(
        document_name=create_document_request.document_name,
        document_type=create_document_request.document_type_id,
        language=create_document_request.language,
        engine=create_document_request.engine,
        llm_type=create_document_request.llm_type,
        blob_name=create_document_request.files[0],
        tenant=get_current_user_organisation(),
        reviewer=ReviewerModel.from_current_user() if create_document_request.assign_to_me else None,
        metadata=create_document_request.metadata,
    )

    return CreateDocumentResponse(document_id=document_id)
