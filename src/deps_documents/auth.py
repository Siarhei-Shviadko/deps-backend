from typing import Any, Dict, Optional

from dependency_injector.wiring import Provide, inject
from fastapi.requests import Request

from deps_documents.containers import Container
from deps_documents.domain.exceptions import AuthError, ForbiddenError
from deps_documents.extras.auth import DepsAuthService
from deps_documents.extras.auth.exceptions import (
    EmptyAuthorizationHeader,
    InvalidAuthorizationHeaderFormat,
    InvalidJWTError,
)
from deps_documents.infrastructure.access_management.context_vars import user

PUBLIC_ENDPOINTS = (
    "/api/document/docs",
    "/api/document/docs/swagger-ui.css",
    "/api/document/openapi.json",
    "/api/document/healthcheck",
    "/api/document/v1/service-info/version",
    "/api/document/v1/debug/500",
    "/favicon.ico",
)


@inject
def set_user_from_jwt(
    request: Request,
    auth_service: DepsAuthService = Provide[Container.services.deps_auth_service],
) -> None:
    if request.url.path not in PUBLIC_ENDPOINTS:
        try:
            user_credentials = auth_service.authorize(request.headers)
            validate_user_organisation(user_credentials)
            user.set(user_credentials)
        except (EmptyAuthorizationHeader, InvalidAuthorizationHeaderFormat) as e:
            raise AuthError(str(e))
        except InvalidJWTError:
            raise AuthError("Invalid JWT")


def validate_user_organisation(decoded_token: Dict[str, Any]) -> None:
    if not is_user_has_one_organisation(decoded_token):
        raise ForbiddenError("User without organisation or with more than one organisation.")


def is_user_has_one_organisation(decoded_token: Dict[str, Any]) -> bool:
    return bool(decoded_token["groups"] and len(decoded_token["groups"]) == 1)


def get_current_user_organisation() -> str:
    current_user = user.get(None)

    return get_user_organisation(current_user)


@inject
def get_user_organisation(
    user_object: Optional[Dict[str, Any]],
    default_organisation: str = Provide[Container.config.authentication.default_organisation],
) -> str:
    if user_object is None:
        return default_organisation

    return user_object["organisation"]
