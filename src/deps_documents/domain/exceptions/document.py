from .common import (
    AlreadyExistsError,
    ContextOperationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


class DocumentForbiddenError(ForbiddenError):
    code = "document_forbidden_error"


class DocumentFileNotFoundError(NotFoundError):
    code = "document_file_not_found"


class PrimaryKeyError(ValidationError):
    code = "invalid_document_primary_key"


class BatchResponseError(ValidationError):
    code = "batch_response_error"


class DocumentExtractDataError(ValidationError):
    code = "document_data_cannot_be_extracted"


class DocumentValidationError(ValidationError):
    code = "document_cannot_be_validated"


class DocumentReviewerError(ValidationError):
    code = "document_reviewer_error"


class DocumentStateError(ValidationError):
    code = "document_state_error"


class DocumentNotAcceptableStateError(ValidationError):
    code = "document_not_acceptable_state_error"


class DocumentReviewStateError(ValidationError):
    code = "document_review_state_error"


class DocumentNotFoundError(NotFoundError):
    code = "document_not_found"


class DocumentAlreadyExistsError(AlreadyExistsError):
    code = "document_already_exists"


class DocumentLastStepRetrievingError(ContextOperationError):
    code = "document_last_step_cannot_be_retried"


class DocumentClassificationError(ContextOperationError):
    code = "document_classification_error"


class DocumentImagesAccessError(ContextOperationError):
    code = "document_images_access_error"


class DocumentAssigningError(ContextOperationError):
    code = "document_assigning_error"

    def __init__(self, doc_ids=None):
        message = f"Can't assign documents." f" One or more documents ({doc_ids}) doesn't exists."
        super().__init__(message)


class AssignedDocumentDeletingError(ContextOperationError):
    code = "assigned_document_deleting_error"

    def __init__(self, doc_ids=None):
        message = f"Can't delete one or more assigned documents." f" One or more documents ({doc_ids}) didn't assigned."
        super().__init__(message)


class DocumentAlreadyAssignedError(ContextOperationError):
    code = "document_already_assigned"

    def __init__(self, doc_ids=None):
        message = f"Can't assign documents." f" One or more documents ({doc_ids}) already assigned."
        super().__init__(message)


class DocumentAlreadyHasDocumentType(ContextOperationError):
    code = "document_already_has_document_type"

    def __init__(self, doc_id: str, doc_type: str) -> None:
        message = f"Document {doc_id} has already had doc type: {doc_type}"
        super().__init__(message)
