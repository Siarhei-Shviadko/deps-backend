from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.detail import (
    ShortDocumentResponseModel,
    ShortDocumentStatusModel,
)
from deps_documents.api.models.document.document import (
    DocumentModel,
    PartialDocumentModel,
)
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(prefix="/{document_id}", route_class=MarkerRoute)


@router.get("", response_model=DocumentModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def get_document_detail(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return DocumentModel.from_domain(document_service.get(document_entity_pk=document_id))


# TODO: add caching
@router.get("/status", response_model=ShortDocumentStatusModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def get_document_status(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return ShortDocumentStatusModel(status=document_service.get(document_entity_pk=document_id).state)


@router.delete("", response_model=bool, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def delete_document(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return document_service.delete(document_entity_pk=document_id)


@router.put("", response_model=ShortDocumentResponseModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def update_document_detail(
    document_id: DocumentEntityPk,
    document: DocumentModel = Body(..., embed=True),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    document.pk = document_id
    return ShortDocumentResponseModel(pk=document_service.update(document.to_domain()))


@router.patch("", response_model=ShortDocumentResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def partial_update_document_detail(
    document_id: DocumentEntityPk,
    document: PartialDocumentModel = Body(...),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    document.pk = document_id
    document_dict = document.model_dump(exclude={"pk"}, by_alias=False, exclude_unset=True)
    document_entity = document.to_domain()
    dict_to_update = {key: document_entity.__getattribute__(key) for key in document_dict.keys()}  # noqa: WPS609
    return ShortDocumentResponseModel(
        pk=document_service.partially_update(
            document_entity_pk=document_id,
            document_fields=dict_to_update,
        ),
    )
