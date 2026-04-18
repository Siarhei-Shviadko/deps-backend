import json
import logging
from typing import Any, Dict, Mapping, Optional, Tuple

from .api_key import APIKeyAuthService
from .deps_jwt import JWTAuthService
from .exceptions import (
    DepsAuthError,
    EmptyAuthorizationHeader,
    InvalidAuthorizationHeaderFormat,
)

__all__ = ["DepsAuthService"]

AUTH_HEADER = "Authorization"
DEPS_TOKEN_HEADER = "deps-token"
JWT_PREFIX = "Bearer "
KEY_PREFIX = "Key "


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class DepsAuthService:
    def __init__(
        self,
        jwt_auth_service: Optional[JWTAuthService] = None,
        api_key_auth_service: Optional[APIKeyAuthService] = None,
        logger: logging.Logger = None,
    ):
        if jwt_auth_service is None and api_key_auth_service is None:
            raise DepsAuthError("Please specify at least one auth service")

        self._jwt_auth_service = jwt_auth_service
        self._api_key_auth_service = api_key_auth_service
        self._logger = logger if logger else _logger

        self._logger.info(
            f"JWTAuthentication enabled: {bool(jwt_auth_service)}"
            f"API key authentication enabled: {bool(api_key_auth_service)}",
        )

    def authorize(self, request_headers: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        deps_token, jwt, key = self.extract_tokens_from_header_string(request_headers)

        if deps_token:
            return self._get_user_credentials_from_json(deps_token, jwt)
        if jwt:
            if self._jwt_auth_service:
                return self._get_user_credentials_from_jwt(jwt)
            else:
                raise DepsAuthError(
                    "Request came with JWT token, but there is no service for handling it. "
                    "Provide JWTAuthService service if it is allowed to authorize with JWT",
                )
        if key:
            if self._api_key_auth_service:
                self._api_key_auth_service.authorize(key)
                return None
            else:
                raise DepsAuthError(
                    "Request came with API key, but there is no service for handling it. "
                    "Provide APIKeyAuthService service if it is allowed to authorize with API key",
                )
        raise DepsAuthError("Request came with invalid credentials")

    @staticmethod
    def extract_tokens_from_header_string(
        request_headers: Mapping[str, str],
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        def extract_from_string(token_string: str) -> str:
            return token_string.split(" ")[1]

        jwt = None
        key = None
        token: Optional[str] = request_headers.get(AUTH_HEADER)
        deps_token: Optional[str] = request_headers.get(DEPS_TOKEN_HEADER)
        if not deps_token and not token:
            raise EmptyAuthorizationHeader("No tokens provided inside Authorization or deps-token headers")
        if token and token.startswith(JWT_PREFIX):
            jwt = extract_from_string(token)
        elif token and token.startswith(KEY_PREFIX):
            key = extract_from_string(token)
        elif not deps_token:
            raise InvalidAuthorizationHeaderFormat(
                "Token formatting is invalid. " "Should start with " f"`{JWT_PREFIX}` or `{KEY_PREFIX}` for jwt or api_key",
            )
        if not deps_token and not jwt and not key:
            raise EmptyAuthorizationHeader("No tokens provided inside Authorization or deps-token headers")
        return deps_token, jwt, key

    def _get_user_credentials_from_jwt(self, token: str) -> Dict[str, Any]:
        if self._jwt_auth_service:
            decoded_token = self._jwt_auth_service.decode(token)
            return {
                "subject": decoded_token["sub"],
                "roles": decoded_token["realm_access"]["roles"],
                "groups": decoded_token["groups"],
                "token": token,
            }
        return {}

    @staticmethod
    def _get_user_credentials_from_json(deps_token: str, token: Optional[str]) -> Dict[str, Any]:
        decoded_token = json.loads(deps_token)
        return {
            "subject": decoded_token["subject"],
            "roles": decoded_token["roles"],
            "groups": decoded_token["groups"],
            "organisation": decoded_token.get("organisation"),
            "email": decoded_token.get("email"),
            "first_name": decoded_token.get("first_name"),
            "last_name": decoded_token.get("last_name"),
            "deps_token": deps_token,
            "token": token,
        }
