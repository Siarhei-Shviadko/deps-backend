from .common import AlreadyExistsError, NotFoundError


class LabelNotFoundError(NotFoundError):
    code = "label_not_found"


class LabelAlreadyExistsError(AlreadyExistsError):
    code = "label_already_exists"


class LabelForDocumentNotFoundError(NotFoundError):
    code = "document_label_not_found"


class LabelForDocumentAlreadyExistsError(AlreadyExistsError):
    code = "label_for_document_already_exists"
