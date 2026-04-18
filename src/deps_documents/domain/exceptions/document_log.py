from .common import AlreadyExistsError


class DocumentLogAlreadyExistsError(AlreadyExistsError):
    code = "document_log_already_exists"
