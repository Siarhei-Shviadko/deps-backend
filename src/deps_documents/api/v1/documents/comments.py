from datetime import datetime, timezone

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.comment import (
    CommentRequestModel,
    CommentResponseModel,
)
from deps_documents.containers import Container
from deps_documents.domain.entities import CommentEntity
from deps_documents.domain.interfaces import IDocumentService
from deps_documents.infrastructure.access_management.context_vars import user

router = APIRouter(route_class=MarkerRoute)


@router.post("/add-comment", response_model=CommentResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def add_comment(
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
    comment: CommentRequestModel = Body(...),
):
    current_user = user.get(None)

    comment_entity = document_service.add_comment(
        comment_entity=CommentEntity(
            text=comment.text,
            created_at=datetime.now(tz=timezone.utc),
            created_by=current_user["subject"] if current_user else None,
        ),
        document_entity_pk=comment.document_id,
    )
    return CommentResponseModel.model_validate(comment_entity)
