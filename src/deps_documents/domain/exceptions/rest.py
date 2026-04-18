from .common import ContextOperationError, DomainError


class ReceiveMessageError(DomainError):
    code = "rabbitmq_recieve_error"


class PublishMessageError(DomainError):
    code = "rabbitmq_publish_error"


class ApplicationEventDispatcherError(DomainError):
    code = "event_dispatcher_error"


class PageNumberError(ContextOperationError):
    code = "out_of_range_page_number"


class DissectionError(ContextOperationError):
    code = "dissection_error"


class DBIntegrityError(ContextOperationError):
    code = "db_integrity_error"
