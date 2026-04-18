from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.strict_str import StrictStr
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(route_class=MarkerRoute)


@router.post("/assign-type", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def batch_assign_type(
    document_ids: list[StrictStr] = Body(..., alias="documentIds", min_length=1),
    type_code: str = Body(None, alias="typeName", min_length=1),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    doc_entities = document_service.assign_type(
        document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in document_ids],
        type_code=type_code,
    )
    return [DocumentModel.from_domain(doc_entity) for doc_entity in doc_entities]
