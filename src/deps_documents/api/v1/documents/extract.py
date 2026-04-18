from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.document.extract import DocumentExtractModel
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(prefix="/extract-data", route_class=MarkerRoute)


@router.post(path="", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def extract_document(
    extract_document_model: DocumentExtractModel,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return [
        DocumentModel.from_domain(x)
        for x in document_service.extract_data(
            document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in extract_document_model.document_ids],
            engine=extract_document_model.engine,
        )
    ]
