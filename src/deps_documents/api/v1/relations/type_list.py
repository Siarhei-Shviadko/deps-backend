from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.list import ListMetaModel
from deps_documents.api.models.relations import (
    RelationResponseModel,
    RelationTypeListResponseModel,
    UpdateRelationTypeResponseModel,
)
from deps_documents.containers import Container
from deps_documents.domain.entities import RelationType
from deps_documents.domain.services import RelationService

router = APIRouter(prefix="/types", route_class=MarkerRoute)


@router.post(
    "",
    response_model=RelationResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def add_relation_type(
    type_: str = Body(..., alias="type", embed=True, min_length=1),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_service.create_relation_type(relation_type=type_)
    return RelationResponseModel(status="created")


@router.get("", response_model=RelationTypeListResponseModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def get_type_list(relation_service: RelationService = Depends(Provide[Container.domain_services.relation])):
    type_list = relation_service.get_relation_type_list()
    return RelationTypeListResponseModel(
        meta=ListMetaModel.model_validate(type_list.meta),
        result=type_list.content,
    )


@router.put(
    "/{relation_type}",
    response_model=UpdateRelationTypeResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def update_type(
    relation_type: str,
    type_: str = Body(..., alias="type", embed=True, min_length=1),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    updated_type = relation_service.update_relation_type(
        relation_type=relation_type,
        type_update_info=RelationType(type_),
    )
    return UpdateRelationTypeResponseModel(type=updated_type)
