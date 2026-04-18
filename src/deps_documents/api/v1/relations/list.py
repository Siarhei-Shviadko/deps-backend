from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.list import ListMetaModel
from deps_documents.api.models.relations import (
    AddRelationResponseModel,
    ListRelationResponseModel,
    RelationModel,
)
from deps_documents.containers import Container
from deps_documents.domain.dtos import RelationFilterObject
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.services import RelationService

router = APIRouter(route_class=MarkerRoute)


@router.post(
    "/",
    response_model=AddRelationResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def add_relation(
    relation: RelationModel,
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = relation_service.create_relation(
        RelationEntity(
            type=relation.type,
            code=relation.code,
            assigned_documents=relation.assigned_documents,
            parent_type=relation.parent_type,
            parent_code=relation.parent_code,
        ),
    )
    return AddRelationResponseModel(relation=RelationModel.model_validate(relation_entity))


@router.get("/", response_model=ListRelationResponseModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def get_relations(
    type_: Optional[str] = Query(None, alias="type"),
    code: Optional[str] = Query(None),
    assigned_documents: Optional[list[int]] = Query(None, alias="assignedDocuments"),
    parent_type: Optional[str] = Query(None, alias="parentType"),
    parent_code: Optional[str] = Query(None, alias="parentCode"),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_list = relation_service.get_relation_list(
        relation=RelationFilterObject(
            type=type_,
            code=code,
            assigned_documents=assigned_documents,
            parent_type=parent_type,
            parent_code=parent_code,
        ),
    )
    return ListRelationResponseModel(
        meta=ListMetaModel.model_validate(relation_list.meta),
        result=[RelationModel.model_validate(relation_entity) for relation_entity in relation_list.content],
    )
