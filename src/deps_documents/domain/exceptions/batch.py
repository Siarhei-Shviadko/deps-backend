from .common import NotFoundError


class BatchIdNotFoundError(NotFoundError):
    code = "batch_id_not_found"
