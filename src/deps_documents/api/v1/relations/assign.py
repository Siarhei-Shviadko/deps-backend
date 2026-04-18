from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.relations import (
    RelationDeleteResponseModel,
    RelationResponseModel,
)
from deps_documents.containers import Container
from deps_documents.domain.constants import AssignAction
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.services import RelationService

router = APIRouter(route_class=MarkerRoute)


@router.post(
    "/{relation_type}/{code}/assign",
    response_model=RelationResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def assign_documents(
    relation_type: str,
    code: str,
    assigned_documents: list[int] = Body(..., alias="assignedDocuments", embed=True),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = RelationEntity(type=relation_type, code=code, assigned_documents=assigned_documents)
    relation_service.assign_document(relation_entity)
    return RelationResponseModel(status="assigned")


@router.delete(
    "/{relation_type}/{code}/assign",
    response_model=RelationDeleteResponseModel,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def remove_assign_documents(
    relation_type: str,
    code: str,
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = RelationEntity(type=relation_type, code=code)
    return RelationDeleteResponseModel(deleted=relation_service.delete_assigned_documents(relation=relation_entity))


@router.patch(
    "/{relation_type}/{code}/assign",
    response_model=RelationResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def patch_assign_documents(
    relation_type: str,
    code: str,
    assigned_documents: list[int] = Body(..., alias="assignedDocuments"),
    action: AssignAction = Body(...),
    relation_service: RelationService = Depends(Provide[Container.domain_services.relation]),
):
    relation_entity = RelationEntity(type=relation_type, code=code, assigned_documents=assigned_documents)
    action_mapping = {
        AssignAction.ADD: relation_service.assign_document,
        AssignAction.DELETE: relation_service.delete_assigned_documents,
    }
    action_function = action_mapping.get(action, None)
    if action_function:
        action_function(relation_entity)  # type: ignore

        return RelationResponseModel(status="patched")

    return RelationResponseModel(status="failed")
