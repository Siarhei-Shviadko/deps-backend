from .common import AlreadyExistsError, NotFoundError


class ReviewerNotFoundError(NotFoundError):
    code = "reviewer_not_found"


class ReviewerAlreadyExistsError(AlreadyExistsError):
    code = "reviewer_already_exists"
