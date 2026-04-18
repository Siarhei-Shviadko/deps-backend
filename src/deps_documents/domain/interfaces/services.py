from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.entities import DocumentEntity, DocumentEntityPk


class IPipelineManagerService(ABC):
    @abstractmethod
    def run(
        self,
        document: DocumentEntity,
        identify_document: bool,
        extract_data: bool,
        extraction_params: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def run_step(
        self,
        document: DocumentEntity,
        step: PipelineStepsEnum,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def run_from_step(
        self,
        document: DocumentEntity,
        step: PipelineStepsEnum,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        pass


class IDataPreProcessService(ABC):
    @abstractmethod
    def execute(self, pks: List[DocumentEntityPk]) -> None:
        pass


class IFileUrlService(ABC):
    @abstractmethod
    def get_external(self, file_path):
        """Returns external url of a file in the file storage service"""

    @abstractmethod
    def get_internal(self, file_path):
        """Returns internal url of a file in the file storage service"""


class IValidationService(ABC):
    @abstractmethod
    def send_document_to_validation(self, document_entity_pk: DocumentEntityPk) -> None:
        pass
