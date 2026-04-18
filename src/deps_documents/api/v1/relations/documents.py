from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.document.list import ListMetaModel
from deps_documents.api.models.relations import DocumentListRelationResponseModel
from deps_documents.containers import Container
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.services import RelationService

router = APIRouter(route_class=MarkerRoute)


@router.get(
    "/{relation_type}/{code}/documents",
    response_model=DocumentListRelationResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_documents(
    relation_type: str,
    code: str,
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    documents = relation_service.get_document(
        RelationEntity(
            type=relation_type,
            code=code,
        ),
    )
    return DocumentListRelationResponseModel(
        meta=ListMetaModel.model_validate(documents.meta),
        result=[DocumentModel.from_domain(relation_entity) for relation_entity in documents.content],
    )
