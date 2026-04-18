from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.analytics import DocumentStateIntervalModel
from deps_documents.containers import Container
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.services import DocumentLogService

router = APIRouter(prefix="/statistic", route_class=MarkerRoute)


@router.get(
    "/states/{document_id}",
    response_model=list[DocumentStateIntervalModel],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_state_statistics(
    document_id: DocumentEntityPk,
    document_log_service: DocumentLogService = Depends(Provide[Container.domain_services.document_log]),
):
    return [
        DocumentStateIntervalModel.model_validate(x) for x in document_log_service.get_document_time_state_intervals(document_id)
    ]
