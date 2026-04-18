from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(prefix="/validate", route_class=MarkerRoute)


@router.post(path="", response_model=DocumentModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def validate(
    document_id: str = Body(..., alias="documentId", embed=True, min_length=1),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return DocumentModel.from_domain(document_service.validate(DocumentEntityPk(document_id)))
