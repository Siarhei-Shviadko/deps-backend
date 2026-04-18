from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.dtos import (
    DocumentFilesDataObject,
    DocumentListDataObject,
    DocumentListFilterObject,
    LabelListFilterObject,
)
from deps_documents.domain.entities import (
    CommentEntity,
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    LabelEntity,
    LabelEntityPk,
    Reviewer,
)


class IDocumentService(ABC):
    @abstractmethod
    def add_comment(self, comment_entity: CommentEntity, document_entity_pk: DocumentEntityPk) -> CommentEntity:
        pass

    @abstractmethod
    def add_file(self, document_entity_pk: DocumentEntityPk, file_content: bytes, file_name: str) -> DocumentEntityPk:
        pass

    @abstractmethod
    def add_label(self, label_pk: LabelEntityPk, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def assign_type(
        self,
        document_entity_pks: List[DocumentEntityPk],
        type_code: Optional[str],
        initial_assign: bool = False,
    ) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def batch_delete(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:
        pass

    @abstractmethod
    def complete_review(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        pass

    @abstractmethod
    def create(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        pass

    @abstractmethod
    def delete(self, document_entity_pk: DocumentEntityPk) -> bool:
        pass

    @abstractmethod
    def document_file(
        self,
        file_content: bytes,
        file_name: str,
        document_name: str,
        source: str,
        run_pipeline: bool,
        language: str,
        engine: str,
        llm_type: Optional[str],
        tenant: Optional[str],
        extraction_params: Optional[Dict[str, Any]] = None,
        document_type: Optional[str] = None,
        sub_type: Optional[str] = None,
        extract_data: bool = False,
        reviewer: Optional[Reviewer] = None,
        metadata: dict[str, Any] = None,
    ) -> DocumentEntityPk:
        pass

    @abstractmethod
    def extract_data(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        pass

    @abstractmethod
    def get_descendants(self, document_entity_pk: DocumentEntityPk, include_containers: bool = False) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get_document_files(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        pass

    @abstractmethod
    def get_document_list(self, options: DocumentListFilterObject) -> DocumentListDataObject:
        pass

    @abstractmethod
    def get_processed_images(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        pass

    @abstractmethod
    def get_brief_documents_info(self, document_pks: list[DocumentEntityPk]) -> list[dict]:
        pass

    @abstractmethod
    def identify(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def remove_label(self, label_pk: LabelEntityPk, document_entity_pk: DocumentEntityPk) -> bool:
        pass

    @abstractmethod
    def get_document_metadata(self, document_entity_pk: DocumentEntityPk) -> DocumentMetadata:
        pass

    @abstractmethod
    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        pass

    @abstractmethod
    def delete_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        pass

    @abstractmethod
    def reset_reviewer(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def retry_last_step(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        pass

    @abstractmethod
    def run_pipeline(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: str,
        language: Optional[str] = None,
        need_extraction: bool = True,
        need_identification: bool = True,
    ) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def run_pipeline_from_step(
        self,
        document_entity_pks: List[DocumentEntityPk],
        step: PipelineStepsEnum,
        language: str,
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def start_review(
        self,
        document_entity_pks: List[DocumentEntityPk],
        reviewer: Optional[Reviewer] = None,
        reassign_reviewer: bool = False,
    ) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def update(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        pass

    @abstractmethod
    def partially_update(
        self,
        document_entity_pk: DocumentEntityPk,
        document_fields: Dict[str, Any],
    ) -> DocumentEntityPk:
        pass

    @abstractmethod
    def update_priorities(self) -> None:
        """
        Recalculates new priority for all documents in database, based on some domain rules
        """
        pass

    @abstractmethod
    def validate(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        pass


class ILabelService(ABC):
    @abstractmethod
    def create(self, label_entity: LabelEntity) -> LabelEntity:
        pass

    @abstractmethod
    def get_list(self, options: LabelListFilterObject) -> List[LabelEntity]:
        pass
