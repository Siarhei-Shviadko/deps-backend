from .common import DomainError


class ServiceProxyError(DomainError):
    code = "service_proxy_error"

    def __init__(self, status_code: int, message: str, service_name: str = None):
        if service_name is not None:
            message = f"{service_name} service says with code {status_code}: {message}"

        super().__init__(message)


class ServiceBadResponseError(DomainError):
    code = "service_bad_response"

    def __init__(self, message: str, service_name: str = None):
        if service_name is not None:
            message = f"Error during validation {service_name} service response: {message}"

        super().__init__(message)


class ValidationServiceConnectionError(DomainError):
    code = "validation_service_connection_error"

    def __init__(self):
        self.message = "Can't connect to the validation service."
        super().__init__(self.message)


class ValidationRequestError(DomainError):
    code = "validation_request_error"

    def __init__(self, msg):
        self.message = f"Error during validation: {msg}"
        super().__init__(self.message)
