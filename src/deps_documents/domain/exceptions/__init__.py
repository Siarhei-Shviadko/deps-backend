from .batch import BatchIdNotFoundError
from .common import (
    AlreadyExistsError,
    AuthError,
    BaseDomainException,
    BusinessException,
    ContextOperationError,
    DomainError,
    DomainException,
    ForbiddenError,
    NonacceptableMimetypeError,
    NotFoundError,
    UnsupportedMimetypeError,
    ValidationError,
)
from .document import (
    AssignedDocumentDeletingError,
    BatchResponseError,
    DocumentAlreadyAssignedError,
    DocumentAlreadyExistsError,
    DocumentAlreadyHasDocumentType,
    DocumentAssigningError,
    DocumentClassificationError,
    DocumentExtractDataError,
    DocumentFileNotFoundError,
    DocumentForbiddenError,
    DocumentImagesAccessError,
    DocumentLastStepRetrievingError,
    DocumentNotAcceptableStateError,
    DocumentNotFoundError,
    DocumentReviewerError,
    DocumentReviewStateError,
    DocumentStateError,
    PrimaryKeyError,
)
from .document_log import DocumentLogAlreadyExistsError
from .document_metadata import DocumentMetadataNotFoundError
from .label import (
    LabelAlreadyExistsError,
    LabelForDocumentAlreadyExistsError,
    LabelForDocumentNotFoundError,
    LabelNotFoundError,
)
from .relation import (
    RelationAlreadyExistsError,
    RelationChildrenNotFoundError,
    RelationFilterError,
    RelationNotFoundError,
    RelationParentNotFoundError,
    RelationTypeAlreadyExistsError,
    RelationTypeNotFoundError,
    RelationTypeUpdatingError,
    RelationUpdatingError,
)
from .rest import (
    ApplicationEventDispatcherError,
    DBIntegrityError,
    DissectionError,
    PageNumberError,
    PublishMessageError,
    ReceiveMessageError,
)
from .reviewer import ReviewerAlreadyExistsError, ReviewerNotFoundError
from .service import (
    ServiceBadResponseError,
    ServiceProxyError,
    ValidationRequestError,
    ValidationServiceConnectionError,
)
from .validation import (
    CoordinatesValidationError,
    FileValidationError,
    InvalidJsonError,
    SchemaValidationError,
)
