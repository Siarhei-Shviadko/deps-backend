from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.label import LabelModel
from deps_documents.containers import Container
from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities import LabelEntity
from deps_documents.domain.services import LabelService

router = APIRouter(prefix="/labels", tags=["Labels"], route_class=MarkerRoute)


@router.get("", response_model=list[LabelModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def get_labels_list(
    label_service: LabelService = Depends(Provide[Container.domain_services_accessor.label]),
) -> list[LabelModel]:
    return [LabelModel.model_validate(label) for label in label_service.get_list(LabelListFilterObject())]


@router.post("", response_model=LabelModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def add_label(
    name: str = Body(..., alias="labelName", embed=True, min_length=1),
    label_service: LabelService = Depends(Provide[Container.domain_services_accessor.label]),
) -> LabelModel:
    return LabelModel.model_validate(label_service.create(label_entity=LabelEntity(name=name)))
