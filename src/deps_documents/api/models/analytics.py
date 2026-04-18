from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from deps_documents.domain.constants import DocumentStateEnum


class DocumentTypeChangeAggregationModel(BaseModel):
    date_time: datetime = Field(alias="startOfDateTimeRange")
    number_of_changed_docs: int = Field(alias="numberOfChangedDocs")
    changed_by: str = Field(alias="changedBy")
    previous_document_type: str = Field(alias="fromType")
    current_document_type: str = Field(alias="toType")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    def model_dump(self, *, by_alias: bool = False, **kwargs) -> dict[str, Any]:
        dict_ = super().model_dump(by_alias=by_alias, **kwargs)
        if by_alias:
            dict_["startOfDateTimeRange"] = dict_["startOfDateTimeRange"].isoformat()
        return dict_


class AnalyticsResponseModel(BaseModel):
    data: list[DocumentTypeChangeAggregationModel]


class DocumentStateIntervalModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    state: DocumentStateEnum
    start_time: datetime = Field(..., alias="startTime")
    finish_time: datetime = Field(..., alias="finishTime")
