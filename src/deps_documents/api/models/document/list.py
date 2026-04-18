# flake8: noqa WPS202
import json
from typing import Any, Optional

from dateutil import parser
from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, conint, field_validator

from deps_documents.api.models.document.detail import ShortDocumentResponseModel
from deps_documents.api.models.document.document import DocumentModel
from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import (
    DateTimeRangeObject,
    DocumentListFilterObject,
    SortingFieldsEnum,
)
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import ValidationError


class ListMetaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    size: int


class ListResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meta: ListMetaModel
    result: list[Any]  # noqa: WPS110


class ListGetDocumentResponseModel(ListResponseModel):
    result: list[DocumentModel]  # noqa: WPS110


class DocumentAddModel(DocumentModel):
    pk: Optional[str] = Field(None, alias="_id")


class DeleteDocumentListResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    deleted_keys: list[ShortDocumentResponseModel] = Field(default_factory=list, alias="deletedDocumentKeys")


_DOCUMENT_VALIDATION_STATUSES = {  # noqa: WPS407
    "passed": {"title": "Passed", "name": "passed"},
    "failed": {"title": "Failed", "name": "failed"},
    "not_applied": {"title": "Not applied", "name": "failed"},
}


def _status_to_validation(status):
    if status:
        if status == _DOCUMENT_VALIDATION_STATUSES["passed"]["title"]:
            return {"succeeded": True}
        if status == _DOCUMENT_VALIDATION_STATUSES["failed"]["title"]:
            return {"succeeded": False}
        if status == _DOCUMENT_VALIDATION_STATUSES["not_applied"]["title"]:
            return {"succeeded": None}
    return {}


def _load_validation_entity(
    validation: Optional[str] = Query(None),
) -> list[dict[str, str]]:
    validation_list = json.loads(validation) if validation else None
    return list(map(_status_to_validation, validation_list)) if validation_list else None


class DocumentListFilterRequestModel(BaseModel):
    states: Optional[str] = Query(None)
    types: Optional[str] = Query(None)
    title: Optional[str] = Query(None)
    except_types: Optional[str] = Query(None, alias="exceptTypes", validation_alias="exceptTypes")
    reviewer: Optional[str] = Query(None)
    sources: Optional[str] = Query(None)
    engines: Optional[str] = Query(None)
    sort_field: SortingFieldsEnum = Query(SortingFieldsEnum.pk, alias="sortField", validation_alias="sortField")
    sort_direct: str = Query("desc", alias="sortDirect", validation_alias="sortDirect")
    page: conint(ge=1) = Query(1)  # type: ignore[valid-type]
    per_page: conint(ge=1) = Query(10, alias="perPage", validation_alias="perPage")  # type: ignore[valid-type]
    labels: Optional[str] = Query(None)
    datetime_range: Optional[str] = Query(None, alias="dateRange", validation_alias="dateRange")
    has_reviewer: Optional[bool] = Query(None, alias="hasReviewer", validation_alias="hasReviewer")
    parent_id: Optional[str] = Query(None, alias="parentId", validation_alias="parentId")
    search: Optional[str] = Query(None)
    filter_ids: Optional[str] = Query(None, alias="filterIds", validation_alias="filterIds")
    groups: Optional[str] = Query(None)

    @field_validator("filter_ids", mode="before")
    def _validate_filter_ids(cls, v: str) -> Optional[str]:  # noqa: N805
        if v is None:
            return None
        try:
            arr = json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("filterIds must be a valid JSON array")
        if not isinstance(arr, list) or len(arr) == 0:
            raise ValueError("filterIds must be a non-empty list")
        for item in arr:
            if not isinstance(item, int):
                raise ValueError("all elements of filterIds must be integers")
        return v

    def to_domain(self) -> DocumentListFilterObject:
        states = json.loads(self.states) if self.states is not None else []
        types = json.loads(self.types) if self.types is not None else []
        except_types = json.loads(self.except_types) if self.except_types is not None else []
        engines = json.loads(self.engines) if self.engines is not None else []
        sources = json.loads(self.sources) if self.sources is not None else []
        labels = json.loads(self.labels) if self.labels is not None else []
        filter_ids = [DocumentEntityPk(x) for x in json.loads(self.filter_ids)] if self.filter_ids is not None else None
        groups = json.loads(self.groups) if self.groups else []

        if not all(
            [state in set(DocumentStateEnum) for state in states],
        ):
            raise ValidationError("Invalid state")

        datetime_range = json.loads(self.datetime_range) if self.datetime_range is not None else None

        return DocumentListFilterObject(
            sort_field=self.sort_field,
            sort_direct=self.sort_direct == "desc",
            page=self.page,
            per_page=self.per_page,
            state=[DocumentStateEnum(state) for state in states],
            document_type=types,
            title=self.title,
            except_types=except_types,
            reviewer=self.reviewer,
            engine=engines,
            source=sources,
            groups=groups,
            labels=labels,
            datetime_range=DateTimeRangeObject(
                start=parser.parse(datetime_range[0]) if isinstance(datetime_range[0], str) else None,
                end=parser.parse(datetime_range[1]) if isinstance(datetime_range[1], str) else None,
            )
            if isinstance(datetime_range, list)
            else None,
            has_reviewer=self.has_reviewer,
            parent_id=self.parent_id,
            search=self.search,
            filter_ids=filter_ids,
        )
