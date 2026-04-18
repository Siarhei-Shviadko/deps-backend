from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

from ..serializers import BriefDocumentInfo, GetBriefDocumentsInfoResponse

router = APIRouter(prefix="/brief-documents-info", route_class=MarkerRoute)


@router.get("", response_model=GetBriefDocumentsInfoResponse, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def get_brief_documents_info(
    document_pks: list[DocumentEntityPk] = Query(..., alias="documentIds"),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    documents = document_service.get_brief_documents_info(document_pks)
    return GetBriefDocumentsInfoResponse(documents=[BriefDocumentInfo.from_dict(document) for document in documents])
