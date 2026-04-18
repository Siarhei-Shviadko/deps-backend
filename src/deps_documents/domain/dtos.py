from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, TypedDict, TypeVar, Union

from deps_documents.domain.constants import (
    DocumentStateEnum,
    RotationEnum,
    TimePeriodEnum,
    UseCaseResponseStatusEnum,
)
from deps_documents.domain.entities import (
    DocumentEntity,
    DocumentEntityPk,
    LabelEntityPk,
    RelationEntity,
    RelationType,
)
from deps_documents.domain.exceptions import DomainException


@dataclass
class BatchResponseObject:
    updated_documents: List[DocumentEntityPk]
    invalid_documents: List[DocumentEntityPk]


@dataclass
class FullBatchResponseObject:
    updated_documents: List[DocumentEntityPk]
    skipped_documents: List[DocumentEntityPk]
    invalid_documents: List[DocumentEntityPk]


class SortingFieldsEnum(Enum):
    pk = "pk"
    title = "title"
    state = "state"
    document_type = "documentType"
    date = "date"
    source = "source"
    reviewer = "reviewer"
    engine = "engine"
    group = "group"


@dataclass
class DateTimeRangeObject:
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class PerPageOptions(Enum):
    FETCH_ALL_DOCS = auto()


@dataclass
class DocumentListFilterObject:
    sort_field: SortingFieldsEnum = SortingFieldsEnum.pk
    sort_direct: bool = True

    page: int = 1
    per_page: Union[int, PerPageOptions] = 10  # FETCH_ALL_DOCS used for fetch all documents

    state: List[DocumentStateEnum] = field(default_factory=list)
    document_type: List[str] = field(default_factory=list)
    title: Optional[str] = None
    except_types: List[str] = field(default_factory=list)
    reviewer: Optional[str] = None
    engine: List[str] = field(default_factory=list)
    source: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)

    labels: List[str] = field(default_factory=list)

    datetime_range: Optional[DateTimeRangeObject] = None
    has_reviewer: Optional[bool] = None

    parent_id: Optional[str] = None

    ids: Optional[List[DocumentEntityPk]] = None
    filter_ids: Optional[List[DocumentEntityPk]] = None

    search: Optional[str] = None


T = TypeVar("T")


@dataclass
class UseCaseResponseObject(Generic[T]):  # pylint: disable=unsubscriptable-object
    status: UseCaseResponseStatusEnum
    error: Optional[DomainException]
    value: Optional[T]

    @classmethod
    def build_success(cls, value: T) -> "UseCaseResponseObject[T]":
        return cls(
            status=UseCaseResponseStatusEnum.SUCCESS,
            value=value,
            error=None,
        )

    @classmethod
    def build_error(cls, error: DomainException) -> "UseCaseResponseObject[T]":
        return cls(
            status=UseCaseResponseStatusEnum.ERROR,
            value=None,
            error=error,
        )


@dataclass
class CoordinateBox:
    top: int
    left: int
    width: int
    height: int


@dataclass
class ExtractDataAreaResponseObject:
    recognized: List[Any]


@dataclass
class DocumentTypeChangeFilter:
    old_type: Optional[str] = None
    new_type: Optional[str] = None
    changed_by: Optional[str] = None
    date_range: Optional[DateTimeRangeObject] = None
    aggregation_period: Optional[TimePeriodEnum] = TimePeriodEnum.HOUR


@dataclass
class DocumentTypeChangeAggregation:
    date_time: datetime
    number_of_changed_docs: int
    changed_by: str
    previous_document_type: str
    current_document_type: str


@dataclass
class TableCell:
    coordinates: CoordinateBox


@dataclass
class TableRow:
    cells: List[TableCell]


@dataclass
class Table:
    coordinates: CoordinateBox
    rows: List[TableRow]


@dataclass
class ExtractLabeledTableResponseObject:
    recognized: List[Any]


@dataclass
class TransformationObject:
    rotation: RotationEnum


@dataclass
class TableDetectionResponseObject:
    recognized: List[Any]


@dataclass
class TrainingInput:
    train_document_ids: List[DocumentEntityPk]
    validate_document_ids: List[DocumentEntityPk]


@dataclass
class EngineObject:
    code: str
    name: str


@dataclass
class TransformCoordinatesResponseObject:
    transformed: List[List[Dict[str, Any]]]


@dataclass
class BlobObject:
    file_name: str
    blob_name: str


@dataclass
class EmailFileParserResponseObject:
    subject: str
    sender: str
    recipients: List[str]
    cc: List[str]
    body: str
    date: str
    attachments: List[BlobObject]


@dataclass
class ListResponseMetaDataObject:
    total: int
    size: int


@dataclass
class DocumentListDataObject:
    meta: ListResponseMetaDataObject
    content: List[DocumentEntity]


@dataclass
class DocumentFilesDataObject:
    files_names: List[str]
    document_name: str


@dataclass
class RelationDataObject:
    meta: ListResponseMetaDataObject
    content: List[RelationEntity]


@dataclass
class RelationTypeDataObject:
    meta: ListResponseMetaDataObject
    content: List[RelationType]


@dataclass
class RelationFilterObject:
    type: Optional[str] = None
    code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    assigned_documents: List[int] = field(default_factory=list)
    parent_type: Optional[str] = None
    parent_code: Optional[str] = None


@dataclass
class UpdateRelationEntity(RelationEntity):
    type: Optional[str] = None
    code: Optional[str] = None


@dataclass
class LabelListFilterObject:
    pks: Optional[List[LabelEntityPk]] = None
    name: Optional[str] = None


class GroupInfo(TypedDict):
    id: str
    tenant_id: str
    name: str
    is_deleted: bool
