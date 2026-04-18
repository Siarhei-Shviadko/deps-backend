from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Optional, TypedDict

from deps_message_flow.commands.common import Command

__all__ = ["SaveBatchDocuments", "SaveBatchDocumentsReply", "SaveBatchDocumentsReplyBuilder"]


class _ProcessingParametersDict(TypedDict, total=False):
    engine: Optional[str]
    language: Optional[str]
    llm_type: Optional[str]
    parsing_features: Optional[list[str]]


class _FileData(TypedDict):
    id: str
    path: str
    name: str
    document_type_id: str
    processing_params: _ProcessingParametersDict
    metadata: dict[str, Any]


@dataclass
class SaveBatchDocuments(Command):
    batch_id: str
    group_id: str
    files: list[_FileData]


class _ErrorInfo(TypedDict):
    message: str
    code: str


class _FileInfo(TypedDict):
    id: str
    document_id: Optional[str]
    error: Optional[_ErrorInfo]


@dataclass
class SaveBatchDocumentsReply(Command):
    batch_id: str
    files: list[_FileInfo]


class SaveBatchDocumentsReplyBuilder:
    batch_id: str
    files: list[_FileInfo]

    def __init__(self, batch_id: str) -> None:
        self.batch_id = batch_id
        self.files: list[_FileInfo] = []

    @contextmanager
    def with_file(self, file_id: str) -> Generator["_FileInfoBuilder", None, "SaveBatchDocumentsReplyBuilder"]:
        file_builder = self._FileInfoBuilder(file_id)
        yield file_builder
        self.files.append(file_builder.build())
        return self

    def build(self) -> SaveBatchDocumentsReply:
        return SaveBatchDocumentsReply(batch_id=self.batch_id, files=self.files)

    class _FileInfoBuilder:
        def __init__(self, file_id: str):
            self.file_id = file_id
            self.document_id: Optional[str] = None
            self.error: Optional[_ErrorInfo] = None

        def with_document_id(self, document_id: str) -> "SaveBatchDocumentsReplyBuilder._FileInfoBuilder":
            self.document_id = document_id
            return self

        def with_error(self, error: Exception) -> "SaveBatchDocumentsReplyBuilder._FileInfoBuilder":
            self.error = _ErrorInfo(code=getattr(error, "code", "no code"), message=f"{error!r}")
            return self

        def build(self) -> "_FileInfo":
            return _FileInfo(id=self.file_id, document_id=self.document_id, error=self.error)
