from abc import abstractmethod
from typing import Generic, TypeVar

from deps_documents.domain.dtos import UseCaseResponseObject

T_req = TypeVar("T_req")
T_res = TypeVar("T_res")


# TODO: remove this
class IUseCase(Generic[T_req, T_res]):
    @abstractmethod
    def execute(self, request_object: T_req) -> UseCaseResponseObject[T_res]:
        pass
