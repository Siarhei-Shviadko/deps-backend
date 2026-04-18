from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Path, Query

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.list import ListMetaModel
from deps_documents.api.models.relations import (
    AddRelationResponseModel,
    ListRelationResponseModel,
    RelationDeleteResponseModel,
    RelationModel,
)
from deps_documents.api.models.relations.detail import RelationPutModel
from deps_documents.containers import Container
from deps_documents.domain.dtos import RelationFilterObject, UpdateRelationEntity
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.services import RelationService

router = APIRouter(route_class=MarkerRoute)


@router.post(
    "/{relation_type}/{code}",
    response_model=AddRelationResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def add_relation(
    relation_type: str,
    code: str,
    assigned_documents: list[int] = Body(..., alias="assignedDocuments"),
    parent_type: Optional[str] = Body(None, alias="parentType"),
    parent_code: Optional[str] = Body(None, alias="parentCode"),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation = relation_service.create_relation(
        RelationEntity(
            type=relation_type,
            code=code,
            assigned_documents=assigned_documents,
            parent_type=parent_type,
            parent_code=parent_code,
        ),
    )
    return AddRelationResponseModel(relation=RelationModel.model_validate(relation))


@router.get(
    "/{relation_type}/{code}",
    response_model=ListRelationResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_relations_by_type_and_code(
    relation_type: str,
    code: str,
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_list = relation_service.get_relation_list(
        relation=RelationFilterObject(
            type=relation_type,
            code=code,
        ),
    )
    return ListRelationResponseModel(
        meta=ListMetaModel.model_validate(relation_list.meta),
        result=[RelationModel.model_validate(relation_entity) for relation_entity in relation_list.content],
    )


@router.delete(
    "/{relation_type}/{code}",
    response_model=RelationDeleteResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def remove_documents(
    relation_type: str,
    code: str,
    doc_id: int = Query(None),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = RelationEntity(
        type=relation_type,
        code=code,
        assigned_documents=[doc_id] if doc_id else [],
    )
    return RelationDeleteResponseModel(
        deleted=relation_service.delete_relation(relation=relation_entity),
    )


@router.put("/{relation_type}/{code}", response_model=RelationModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def update_relation(
    relation_type: str = Path(...),
    code: str = Path(...),
    relation_model: RelationPutModel = Body(...),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = relation_service.update(
        RelationEntity(
            type=relation_type,
            code=code,
            assigned_documents=relation_model.assigned_documents,
            parent_type=relation_model.parent_type,
            parent_code=relation_model.parent_code,
        ),
        UpdateRelationEntity(
            type=relation_model.code,
            code=relation_model.type,
            assigned_documents=relation_model.assigned_documents,
            parent_type=relation_model.parent_type,
            parent_code=relation_model.parent_code,
        ),
    )
    return RelationModel.model_validate(relation_entity)
