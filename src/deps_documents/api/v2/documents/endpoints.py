from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, UploadFile
from pydantic import Json

from deps_documents.application import DocumentAccessServiceV3 as DocumentAccessService
from deps_documents.auth import get_current_user_organisation
from deps_documents.containers import Container
from deps_documents.domain.entities import LabelEntityPk, ParsingFeature

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...parsers import get_label_ids, get_parsing_features
from .serializers import CreateDocumentResponse

__all__ = ["document_router"]


document_router = APIRouter(
    tags=["Documents"],
    route_class=MarkerRoute,
    prefix="/documents",
)


@document_router.post(
    "",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=CreateDocumentResponse,
)
@inject
def create_document(
    document_name: str = Body(..., alias="documentName"),
    tenant_id: str = Depends(get_current_user_organisation),
    document_type_id: Optional[str] = Body(default=None, alias="documentType"),
    group_id: Optional[str] = Body(default=None, alias="groupId"),
    file: UploadFile = File(...),
    engine: Optional[str] = Body(default=None),
    language: Optional[str] = Body(default=None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    parsing_features: Optional[set[ParsingFeature]] = Depends(get_parsing_features),
    needs_unification: bool = Body(default=True, alias="needsUnifier"),
    needs_extraction: bool = Body(default=True, alias="needsExtraction"),
    needs_parsing: Optional[bool] = Body(default=None, alias="needsParsing"),
    needs_validation: Optional[bool] = Body(default=None, alias="needsValidation"),
    needs_review: Optional[str] = Body(default=None, alias="needsReview"),
    needs_output_exporting: Optional[bool] = Body(default=None, alias="needsOutputExporting"),
    assign_to_me: bool = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Body(default=None),
    label_ids: Optional[list[LabelEntityPk]] = Depends(get_label_ids),
    document_access_service: DocumentAccessService = Depends(Provide[Container.application.document_access_v3]),
):
    return CreateDocumentResponse(
        document_id=document_access_service.create_document(
            document_name=document_name,
            document_type_id=document_type_id if document_type_id else None,
            group_id=group_id if group_id else None,
            tenant_id=tenant_id,
            file_name=file.filename,
            file_content=file.file.read(),
            engine=engine if engine else None,
            language=language if language else None,
            llm_type=llm_type if llm_type else None,
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            metadata=metadata if metadata else None,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_review=needs_review,
            needs_output_exporting=needs_output_exporting,
            label_ids=label_ids,
        ),
    )
