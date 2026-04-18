import os
from enum import Enum, auto


class UseCaseResponseStatusEnum(str, Enum):
    SUCCESS = auto()
    ERROR = auto()


class PipelineStepsEnum(str, Enum):
    PREPROCESS = "preprocess"
    IDENTIFICATION = "identification"
    EXTRACTION = "extraction"


class TrainingPipelineStepsEnum(str, Enum):
    EXTRACTION_TRAINING = "extraction_training"


class DocumentStateEnum(str, Enum):
    NEW = "new"
    PREPROCESSING = "preprocessing"
    IDENTIFICATION = "identification"
    DATA_EXTRACTION = "dataExtraction"
    VALIDATION = "validation"
    IN_REVIEW = "inReview"
    FAILED = "failed"
    COMPLETED = "completed"

    # new states
    UNIFICATION = "unification"
    IMAGE_PREPROCESSING = "imagePreprocessing"
    PARSING = "parsing"
    VERSION_IDENTIFICATION = "versionIdentification"
    POSTPROCESSING = "postprocessing"
    NEEDS_REVIEW = "needsReview"
    EXPORTING = "exporting"
    EXPORTED = "exported"
    EXCEPTIONAL_QUEUE = "exceptionalQueue"
    POSTPONED = "postponed"


class DocumentLogEnum(str, Enum):
    TYPE_CHANGED = "typeChanged"
    STATE_CHANGED = "stateChanged"
    REVIEWER_CHANGED = "reviewerChanged"
    VALIDATION_SKIPPED = "validationSkipped"


class FieldTypeEnum(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    ENUM = "enum"
    COORDINATES = "coordinates"
    CHECKBOX = "checkbox"
    LIST = "list"
    DICT = "dict"
    TABLE = "table"

    def __str__(self):
        return str(self.value)


SKIP_VALIDATION_STATES = [
    DocumentStateEnum.IN_REVIEW,
]

START_REVIEW_STATES = [
    DocumentStateEnum.COMPLETED,
    DocumentStateEnum.NEEDS_REVIEW,
]

FIELDS_SECTION_NAME = "Fields"
FIELDS_SECTION_TITLE = "Fields"
TABLE_SECTION_NAME = "TableData"
TABLE_SECTION_TITLE = "Table Data"
API_NUMBER_FIELD_NAME = "apiNumber"

PROCESSING_STATES = [
    DocumentStateEnum.PREPROCESSING,
    DocumentStateEnum.IDENTIFICATION,
    DocumentStateEnum.DATA_EXTRACTION,
]

UNACCEPTABLE_IDENTIFICATION_DOCUMENT_STATES = [
    DocumentStateEnum.NEW,
    DocumentStateEnum.PREPROCESSING,
    DocumentStateEnum.IDENTIFICATION,
    DocumentStateEnum.DATA_EXTRACTION,
]

DOCUMENT_ERROR_STATES = [
    DocumentStateEnum.FAILED,
    DocumentStateEnum.EXCEPTIONAL_QUEUE,
    DocumentStateEnum.POSTPONED,
]

END_STATES = [
    DocumentStateEnum.FAILED,
    DocumentStateEnum.EXCEPTIONAL_QUEUE,
    DocumentStateEnum.POSTPONED,
    DocumentStateEnum.COMPLETED,
]


class CharTypeEnum(str, Enum):
    NUMERIC = "numeric"
    ALPHABETIC = "alphabetic"
    ALPHANUMERIC = "alphanumeric"
    BOOLEAN = "boolean"

    def __str__(self):
        return str(self.value)


class TimePeriodEnum(str, Enum):
    DAY = "day"
    HOUR = "hour"


class ActorEnum(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"


class RotationEnum(int, Enum):
    ROTATE_90_COUNTERCLOCKWISE = -90
    ROTATE_90_CLOCKWISE = 90
    ROTATE_180 = 180


class DocumentExportTypesEnum(str, Enum):
    XML = "xml"
    JSON = "json"
    DOCX = "docx"


class DocumentTemplateStateEnum(str, Enum):
    NEW = "new"
    PREPROCESSING = "preprocessing"
    READY = "ready"
    FAILED = "failed"


class DocumentAssignmentStatusEnum(str, Enum):
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    HOLD = "hold"


class DocumentPriorityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExtractionTypeEnum(str, Enum):
    ML = "ml"
    TEMPLATE = "template"
    PULLABLE_ML = "pullable_ml"


class ContainerTypesEnum(str, Enum):
    EMAIL = "email"


class EmailFileExtensionEnum(str, Enum):
    EML = "eml"
    MSG = "msg"


class AssignAction(str, Enum):
    ADD = "add"
    DELETE = "delete"


AUTH_ACCESS_TOKEN_NAME_TEMPLATE = "access_token_{}"  # noqa: S105
AUTH_SESSION_JWK_TEMPLATE = "{}jwk"
DEPS_REDIRECT_COOKIE = "DEPSREDIRECT"


class LoginTypesEnum(Enum):
    CREDENTIALS = auto()
    OAUTH = auto()


class RolesEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ErrorType(str, Enum):
    SYSTEM = "system"
    BUSINESS = "business"


class DocumentProcessingResult(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def from_state(cls, state: DocumentStateEnum):
        if state in DOCUMENT_ERROR_STATES:
            return cls.FAILED
        if state == DocumentStateEnum.COMPLETED:
            return cls.COMPLETED
        raise RuntimeError("Attempting to get processing result for unfinished pipeline")


PATH_TO_SAMPLE_DOCUMENTS = os.path.abspath("/app/data/sample_documents")

SAMPLE_DOCUMENTS = [
    {
        "sample_id": 0,
        "file_name": "OCR Sample 1.pdf",
        "file_path": f"{PATH_TO_SAMPLE_DOCUMENTS}/OCR Sample.pdf",
        "language": "eng",
        "engine": "TESSERACT",
    },
    {
        "sample_id": 1,
        "file_name": "OCR Sample 2.pdf",
        "file_path": f"{PATH_TO_SAMPLE_DOCUMENTS}/OCR Sample.pdf",
        "language": "eng",
        "engine": "EASYOCR",
    },
    {
        "sample_id": 2,
        "file_name": "NER Sample.png",
        "file_path": f"{PATH_TO_SAMPLE_DOCUMENTS}/NER Sample.png",
        "language": "eng",
        "engine": "TESSERACT",
    },
    {
        "sample_id": 3,
        "file_name": "Table Sample 1.png",
        "file_path": f"{PATH_TO_SAMPLE_DOCUMENTS}/Table_Sample_1.png",
        "language": "eng",
        "engine": "TESSERACT",
    },
    {
        "sample_id": 4,
        "file_name": "Table Sample 2.jpg",
        "file_path": f"{PATH_TO_SAMPLE_DOCUMENTS}/Table_Sample_2.jpg",
        "language": "eng",
        "engine": "EASYOCR",
    },
]
