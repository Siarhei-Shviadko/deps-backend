from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.strict_str import StrictStr
from deps_documents.containers import Container
from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService

router = APIRouter(route_class=MarkerRoute)


@router.post("/run-pipeline", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def run_pipeline(
    document_ids: list[StrictStr] = Body(..., alias="documentIds", min_length=1),
    engine: Optional[str] = Body(None, alias="engineName"),
    language: str = Body("eng"),
    extract_data: bool = Body(default=True, alias="extractData"),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return [
        DocumentModel.from_domain(doc_entity)
        for doc_entity in document_service.run_pipeline(
            document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in document_ids],
            engine=engine,
            language=language,
            need_extraction=extract_data,
        )
    ]


@router.post("/run-pipeline-from-step", response_model=list[DocumentModel], openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def run_pipeline_from_step(
    document_ids: list[StrictStr] = Body(..., alias="documentIds", min_length=1),
    step: PipelineStepsEnum = Body(...),
    engine: Optional[str] = Body(None, alias="engineName"),
    language: str = Body(default="eng"),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return [
        DocumentModel.from_domain(doc_entity)
        for doc_entity in document_service.run_pipeline_from_step(
            document_entity_pks=[DocumentEntityPk(doc_id) for doc_id in document_ids],
            step=step,
            engine=engine,
            language=language,
        )
    ]


@router.post("/retry-last-step", response_model=DocumentModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def retry_last_step(
    document_id: str = Body(..., alias="documentId", min_length=1, embed=True),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    return DocumentModel.from_domain(document_service.retry_last_step(document_entity_pk=DocumentEntityPk(document_id)))
