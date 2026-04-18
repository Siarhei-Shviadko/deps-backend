import logging
from http import HTTPStatus
from json import JSONDecodeError

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request

from deps_documents.api.models.error import ErrorModel
from deps_documents.domain.exceptions import (
    AlreadyExistsError,
    AuthError,
    BaseDomainException,
    ContextOperationError,
    DocumentFileNotFoundError,
    DomainError,
    DomainException,
    ForbiddenError,
    NonacceptableMimetypeError,
    NotFoundError,
    RelationNotFoundError,
    UnsupportedMimetypeError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def json_domain_error_handler(error: BaseDomainException, status_code: int):
    return JSONResponse(status_code=status_code, content=ErrorModel(code=error.code, message=str(error)).model_dump())


def register_errorhandler(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, error: DomainError):  # noqa: WPS430
        return json_domain_error_handler(error, HTTPStatus.INTERNAL_SERVER_ERROR)

    @app.exception_handler(DomainException)
    def handle_domain_exception(request: Request, error: DomainException):  # noqa: WPS430
        mapper = [
            (ValidationError, HTTPStatus.BAD_REQUEST),
            (AuthError, HTTPStatus.UNAUTHORIZED),
            (ForbiddenError, HTTPStatus.FORBIDDEN),
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (NonacceptableMimetypeError, HTTPStatus.NOT_ACCEPTABLE),
            (AlreadyExistsError, HTTPStatus.CONFLICT),
            (UnsupportedMimetypeError, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
            (ContextOperationError, HTTPStatus.BAD_REQUEST),
            (RelationNotFoundError, HTTPStatus.NOT_FOUND),
            (DocumentFileNotFoundError, HTTPStatus.NOT_FOUND),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_domain_error_handler(error, status_code)

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):  # noqa: WPS430
        message = str(jsonable_encoder(exc.errors()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorModel(code="request_validation_error", message=message).model_dump(),
        )

    @app.exception_handler(JSONDecodeError)
    def json_decode_exception_handler(request: Request, exc: JSONDecodeError):  # noqa: WPS430
        message = str(jsonable_encoder(exc.msg))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorModel(code="json_decode_error", message=message).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(request: Request, error: Exception):  # noqa: WPS430
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorModel(code="unhandled_error", message=str(error)).model_dump(),
        )
