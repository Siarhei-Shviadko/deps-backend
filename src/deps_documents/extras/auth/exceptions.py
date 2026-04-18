class DepsAuthError(Exception):
    pass


class JWTAuthServiceError(DepsAuthError):
    pass


class InvalidJWTError(DepsAuthError):
    pass


class InvalidAPIKey(DepsAuthError):
    def __init__(self):
        super().__init__("API Key is invalid")


class EmptyAuthorizationHeader(DepsAuthError):
    pass


class InvalidAuthorizationHeaderFormat(DepsAuthError):
    pass
