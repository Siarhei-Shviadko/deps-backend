class BaseDomainException(Exception):
    code = "base domain_exception"


class BusinessException(BaseDomainException):
    code = "business exception"


class DomainException(BaseDomainException):
    code = "domain_exception"


class DomainError(BaseDomainException):
    code = "domain_error"


class AlreadyExistsError(DomainException):
    code = "already_exists_error"


class NotFoundError(DomainException):
    code = "not_found_error"


class ContextOperationError(DomainException):
    code = "context_operation_error"


class ValidationError(DomainException):
    code = "validation_error"


class ServiceError(DomainException):
    code = "service_error"


class AuthError(DomainException):
    code = "authentication_error"


class UnsupportedMimetypeError(DomainException):
    code = "unsupported_mimetype_error"


class NonacceptableMimetypeError(DomainException):
    code = "nonacceptable_mimetype_error"


class ForbiddenError(DomainException):
    code = "forbidden_error"
