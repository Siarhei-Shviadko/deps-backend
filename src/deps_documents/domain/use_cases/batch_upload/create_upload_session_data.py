from dataclasses import dataclass

from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.interfaces import IBatchUploadDataRepository, IUseCase


# TODO: refactor by replacing with service
class RequestObject:
    pass  # noqa: WPS420 WPS604


@dataclass
class ResponseObject:
    batch_id: str


class CreateUploadSessionDataUseCase(IUseCase[RequestObject, ResponseObject]):
    def __init__(self, batch_upload_data_repository: IBatchUploadDataRepository):
        self._batch_upload_data_repository = batch_upload_data_repository

    def execute(self, request_object: RequestObject = None) -> UseCaseResponseObject[ResponseObject]:
        batch_id = self._batch_upload_data_repository.create_batch_id()
        response = ResponseObject(batch_id=batch_id)

        return UseCaseResponseObject[ResponseObject].build_success(response)
