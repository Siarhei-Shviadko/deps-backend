from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends
from pydantic import conint, conlist

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.detail import ShortDocumentResponseModel
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.document.list import (
    DeleteDocumentListResponseModel,
    DocumentAddModel,
    DocumentListFilterRequestModel,
    ListGetDocumentResponseModel,
    ListMetaModel,
)
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(prefix="/documents", route_class=MarkerRoute)


@router.get("", response_model=ListGetDocumentResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def get_document_list(  # noqa: WPS234
    documents_filters: DocumentListFilterRequestModel = Depends(),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    doc_list = document_service.get_document_list(options=documents_filters.to_domain())
    return ListGetDocumentResponseModel(
        meta=ListMetaModel.model_validate(doc_list.meta),
        result=[DocumentModel.from_domain(doc_entity) for doc_entity in doc_list.content],
    )


@router.post(
    "",
    response_model=ShortDocumentResponseModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def add_document(
    document: DocumentAddModel = Body(..., embed=True),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return ShortDocumentResponseModel(pk=document_service.create(document.to_domain()))


@router.put("", response_model=ShortDocumentResponseModel, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def update_document_detail(
    document: DocumentModel = Body(..., embed=True),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return ShortDocumentResponseModel(pk=document_service.update(document.to_domain()))


@router.delete("", response_model=DeleteDocumentListResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def delete_document_list(
    document_ids: conlist(conint(ge=1), min_length=1) = Body(..., alias="documentIds", embed=True),  # type: ignore[valid-type]
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return DeleteDocumentListResponseModel(
        deleted_keys=[
            ShortDocumentResponseModel(pk=doc_id)
            for doc_id in document_service.batch_delete(
                document_entity_pks=[DocumentEntityPk(str(doc_id)) for doc_id in document_ids],
            )
        ],
    )
