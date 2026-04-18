from typing import List

from .common import ValidationError


class FileValidationError(ValidationError):
    code = "file_validation"


class CoordinatesValidationError(ValidationError):
    code = "coordinates_validation_error"


class InvalidJsonError(ValidationError):
    code = "invalid_json_error"

    def __init__(self, message: str = None):
        if message is None:
            message = "JSON decode error occurred on deserialization of request parameters"

        super().__init__(message)


class SchemaValidationError(ValidationError):
    code = "schema_validation_error"

    def __init__(self, validation_messages: List[str], message: str = None):
        if message is None:
            message = "There are a problems during matching request-data and schema"
        self.data = validation_messages

        super().__init__(message)
