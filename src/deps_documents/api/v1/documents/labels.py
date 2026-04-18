from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.strict_str import StrictStr
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk, LabelEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(route_class=MarkerRoute)


@router.post("/add-label", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def add_label_batch(
    document_ids: list[StrictStr] = Body(..., alias="documentIds", min_length=1),
    label_id: str = Body(..., alias="labelId", min_length=1),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    label_entities = document_service.add_label(
        label_pk=LabelEntityPk(label_id),
        document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in document_ids],
    )

    return [DocumentModel.from_domain(doc_entity) for doc_entity in label_entities]


@router.post("/remove-label", response_model=bool, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def remove_label(
    document_id: str = Body(..., alias="documentId", min_length=1),
    label_id: str = Body(..., alias="labelId", min_length=1),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return document_service.remove_label(label_pk=LabelEntityPk(label_id), document_entity_pk=DocumentEntityPk(document_id))
