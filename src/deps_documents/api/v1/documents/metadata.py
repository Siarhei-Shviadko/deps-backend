from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.metadata import DocumentMetadataResponseModel
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(prefix="/{document_id}", route_class=MarkerRoute)


@router.get("/metadata", response_model=DocumentMetadataResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def get_document_metadata(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    metadata_entity = document_service.get_document_metadata(document_id)
    return DocumentMetadataResponseModel.model_validate(metadata_entity)
