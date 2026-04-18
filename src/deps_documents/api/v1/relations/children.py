from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.list import ListMetaModel
from deps_documents.api.models.relations.detail import RelationModel
from deps_documents.api.models.relations.list import ListRelationResponseModel
from deps_documents.containers import Container
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.services import RelationService

router = APIRouter(route_class=MarkerRoute)


@router.get(
    "/{relation_type}/{code}/children",
    response_model=ListRelationResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_document_children(
    relation_type: str,
    code: str,
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    children_list = relation_service.get_children_list(
        RelationEntity(
            type=relation_type,
            code=code,
        ),
    )
    return ListRelationResponseModel(
        meta=ListMetaModel.model_validate(children_list.meta),
        result=[RelationModel.model_validate(relation_entity) for relation_entity in children_list.content],
    )
