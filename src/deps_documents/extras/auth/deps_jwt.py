import logging
from functools import lru_cache
from typing import Any, Dict

import requests
from authlib.jose import JsonWebKey, JsonWebToken
from authlib.jose.errors import JoseError

from .exceptions import InvalidJWTError, JWTAuthServiceError

logger = logging.getLogger(__name__)

__all__ = ["JWTAuthService"]


class JWTAuthService:
    """
    Service for validating and decoding jwt tokens.
    Accepts jwt encoded only with RS256.
    """

    def __init__(self, certs_endpoint: str, encryption_algorithm: str, verify_ssl: bool = True):
        """
        certs_endpoint: uri for fetching public keys
        """
        self._certs_endpoint = certs_endpoint
        self._encryption_algorithm = encryption_algorithm
        self._is_ssl_enabled = verify_ssl

        logger.debug(f"Fetching public JWK from {self._certs_endpoint}")
        logger.debug(f"SSL verification enabled = {self._is_ssl_enabled}")

    def decode(self, token: str) -> Dict[str, Any]:
        public_keys = self._fetch_jwks()
        try:
            tok = JsonWebToken([self._encryption_algorithm]).decode(token, key=public_keys)
            tok.validate()
        except JoseError as e:
            logger.debug(e)
            raise InvalidJWTError

        logger.debug("Token validated successfully")
        return tok

    @lru_cache(maxsize=1)
    def _fetch_jwks(self):
        logger.debug("Start fetching public JWK")
        try:
            # SSL verification can be disabled for self-signed certificates
            res = requests.get(self._certs_endpoint, verify=self._is_ssl_enabled)
            res.raise_for_status()
            keys = JsonWebKey.import_key_set(res.json()["keys"])
        except Exception as e:
            logger.exception(e)
            raise JWTAuthServiceError(f"Error has occurred while fetching public JWK on '{self._certs_endpoint}'")
        logger.debug(f"Successfully fetched public JWK from {self._certs_endpoint}")
        return keys
