from dataclasses import asdict
from datetime import datetime
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.api.models.analytics import AnalyticsResponseModel
from deps_documents.containers import Container
from deps_documents.domain.constants import TimePeriodEnum
from deps_documents.domain.dtos import DateTimeRangeObject, DocumentTypeChangeFilter
from deps_documents.domain.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"], route_class=MarkerRoute)


@router.get("/document-type-change", response_model=AnalyticsResponseModel, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def aggregate_by_document_type(
    old_type: str = Query(None, alias="fromType"),
    new_type: str = Query(None, alias="toType"),
    changed_by: str = Query(None, alias="changedBy"),
    aggregation_period: TimePeriodEnum = Query(TimePeriodEnum.HOUR, alias="aggregationPeriod"),
    date_range: Optional[tuple[datetime, datetime]] = Query(None, alias="dateRange"),
    analytics_service: AnalyticsService = Depends(Provide[Container.domain_services.analytics]),
) -> AnalyticsResponseModel:
    filter_obj = DocumentTypeChangeFilter(
        old_type=old_type,
        new_type=new_type,
        changed_by=changed_by,
        date_range=DateTimeRangeObject(start=date_range[0], end=date_range[0]) if date_range else None,
        aggregation_period=aggregation_period,
    )
    aggregation_data = analytics_service.aggregate_document_type_change(filter_obj)
    return AnalyticsResponseModel.model_validate({"data": [asdict(aggregation_obj) for aggregation_obj in aggregation_data]})
