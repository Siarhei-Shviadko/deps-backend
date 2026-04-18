from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, UploadFile
from pydantic import Json

from deps_documents.api.v2.documents.serializers import CreateDocumentFromFileResponse
from deps_documents.application import DocumentAccessServiceV3 as DocumentAccessService
from deps_documents.auth import get_current_user_organisation
from deps_documents.containers import Container
from deps_documents.domain.entities import ParsingFeature

from .parsers import get_parsing_features, parse_metadata

__all__ = ["internal_router"]

internal_router = APIRouter(prefix="/documents")


@internal_router.post(
    "/from-file",
    status_code=HTTPStatus.CREATED,
    response_model=CreateDocumentFromFileResponse,
)
@inject
def create_document_from_file(
    document_name: str = Body(..., alias="documentName"),
    tenant_id: str = Depends(get_current_user_organisation),
    document_type_id: str = Body(..., alias="documentType"),
    group_id: Optional[str] = Body(default=None, alias="groupId"),
    file: UploadFile = File(...),
    engine: Optional[str] = Body(default=None),
    language: Optional[str] = Body(default=None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    parsing_features: Optional[set[ParsingFeature]] = Depends(get_parsing_features),
    needs_unification: bool = Body(default=True, alias="needsUnifier"),
    needs_extraction: bool = Body(default=True, alias="needsExtraction"),
    needs_parsing: bool = Body(default=False, alias="needsParsing"),
    assign_to_me: bool = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Depends(parse_metadata),
    document_access_service: DocumentAccessService = Depends(Provide[Container.application.document_access_v3]),
) -> CreateDocumentFromFileResponse:
    document_id, document_name = document_access_service.create_document_from_file(
        document_name=document_name,
        document_type_id=document_type_id,
        group_id=group_id if group_id else None,
        tenant_id=tenant_id,
        file_name=file.filename,
        file_content=file.file.read(),
        engine=engine if engine else None,
        language=language if language else None,
        llm_type=llm_type if llm_type else None,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_parsing=needs_parsing,
    )

    return CreateDocumentFromFileResponse(
        document_id=document_id,
        document_name=document_name,
    )
