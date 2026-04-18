from http import HTTPStatus
from typing import Any, Dict, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from fastapi.exceptions import HTTPException
from pydantic import Json, ValidationError

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.document.extract import ExtractionParams
from deps_documents.api.models.document.reviewer import ReviewerModel
from deps_documents.api.models.document.upload import (
    MultiUploadSessionResponseModel,
    UploadFileResponseModel,
)
from deps_documents.auth import get_current_user_organisation
from deps_documents.containers import Container
from deps_documents.domain.constants import UseCaseResponseStatusEnum
from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService, IUseCase
from deps_documents.infrastructure.synchronisation import SynchronisationRegistry

router = APIRouter(route_class=MarkerRoute)


# TODO: remove this
def _default_use_case_response_handler(response: UseCaseResponseObject) -> None:
    use_case_error = response.error

    if response.status == UseCaseResponseStatusEnum.ERROR:
        raise use_case_error


@router.post(
    "/multi-upload-session",
    response_model=MultiUploadSessionResponseModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_upload_session(upload_usecase: IUseCase = Depends(Provide[Container.use_cases.create_upload_session])):
    upload_result = upload_usecase.execute()  # type: ignore
    return MultiUploadSessionResponseModel(batch_id=upload_result.value.batch_id)


def get_extraction_params(
    extraction_params: Optional[Json] = Form(None, alias="extractionParams"),
) -> Dict[str, Any]:
    if not extraction_params:
        return {}
    try:
        return ExtractionParams(**extraction_params).model_dump()
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors())


# TODO: totally remove source
@router.post("/document-file", response_model=UploadFileResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def upload_file(  # noqa: WPS210, WPS212 - should be removed after refactoring
    file: UploadFile = File(...),
    document_name: Optional[str] = Body(None, alias="documentName"),
    batch_id: Optional[str] = Body(None, alias="batchId"),
    run_pipeline: Optional[bool] = Body(None, alias="runPipeline"),
    language: Optional[str] = Body(None),
    engine: Optional[str] = Body(None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    document_type: Optional[str] = Body(None, alias="documentType"),
    sub_type: Optional[str] = Body(None, alias="modelName"),
    extract_data: bool = Body(default=True, alias="extractData"),
    extraction_params: Dict[str, Any] = Depends(get_extraction_params),
    get_batch_upload_data_usecase: IUseCase = Depends(Provide[Container.use_cases.get_batch_upload_data]),
    update_batch_upload_data_usecase: IUseCase = Depends(Provide[Container.use_cases.update_batch_upload_data]),
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
    syncronisation: SynchronisationRegistry = Depends(Provide[Container.synchronisaction.registry]),
    assigned_to_me: bool = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Body(default=None),
    current_tenant: str = Depends(get_current_user_organisation),
):
    def _has_batch_started(batch_id_to_check: str) -> bool:  # noqa: WPS430
        use_case = get_batch_upload_data_usecase
        get_batch_data_request = use_case.Request(batch_id=batch_id_to_check)  # type: ignore

        use_case_response = use_case.execute(get_batch_data_request)
        _default_use_case_response_handler(use_case_response)
        batch_upload_data = use_case_response.value.batch_upload_data
        return batch_upload_data.get("document_id", None) is not None

    def _set_document_id_for_batch_id(batch_id_to_add: str, existed_doc_id: str) -> None:  # noqa: WPS430
        batch_upload_data = {"document_id": existed_doc_id}
        use_case = update_batch_upload_data_usecase
        update_batch_data_request = use_case.Request(  # type: ignore
            batch_id=batch_id_to_add,
            batch_upload_data=batch_upload_data,
        )

        use_case_response = use_case.execute(update_batch_data_request)
        _default_use_case_response_handler(use_case_response)

    def _get_document_id_for_batch_id(existed_batch_id: str) -> str:  # noqa: WPS430
        use_case = get_batch_upload_data_usecase
        get_batch_data_request = use_case.Request(batch_id=existed_batch_id)  # type: ignore

        use_case_response = use_case.execute(get_batch_data_request)
        _default_use_case_response_handler(use_case_response)
        batch_upload_data = use_case_response.value.batch_upload_data
        return batch_upload_data.get("document_id", None)

    def _add_file_to_document(existed_doc_id: str) -> UploadFileResponseModel:  # noqa: WPS430
        doc_id = document_service.add_file(
            document_entity_pk=DocumentEntityPk(existed_doc_id),
            file_content=file.file.read(),
            file_name=file.filename,
        )
        return UploadFileResponseModel(
            document_id=doc_id,
            message=f"File to the document {doc_id} successfully added",
        )

    def _add_document() -> UploadFileResponseModel:  # noqa: WPS430
        reviewer = ReviewerModel.from_current_user() if assigned_to_me else None
        doc_file = document_service.document_file(
            file_content=file.file.read(),
            file_name=file.filename,
            document_name=document_name,
            source=None,  # type: ignore
            run_pipeline=run_pipeline,
            language=language,
            engine=engine,
            llm_type=llm_type,
            tenant=current_tenant,
            document_type=document_type,
            sub_type=sub_type,
            extract_data=extract_data,
            extraction_params=extraction_params,
            reviewer=reviewer,
            metadata=metadata,
        )

        return UploadFileResponseModel(
            document_id=doc_file,
            message=f"Document {doc_file} successfully added",
        )

    with syncronisation.named_lock(batch_id):
        if batch_id and _has_batch_started(batch_id):
            document_id = _get_document_id_for_batch_id(batch_id)
            doc_file = _add_file_to_document(document_id)
        else:
            doc_file = _add_document()
            if batch_id:
                _set_document_id_for_batch_id(batch_id, doc_file.document_id)

    return doc_file
