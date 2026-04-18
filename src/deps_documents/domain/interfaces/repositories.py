from abc import ABC, abstractmethod
from typing import Dict, List

from deps_documents.domain.dtos import (
    DocumentListFilterObject,
    DocumentStateEnum,
    DocumentTypeChangeAggregation,
    DocumentTypeChangeFilter,
    GroupInfo,
    LabelListFilterObject,
    RelationFilterObject,
    UpdateRelationEntity,
)
from deps_documents.domain.entities import (
    CommentEntity,
    DocumentEntity,
    DocumentEntityPk,
    DocumentLogEntity,
    DocumentMetadata,
    DocumentTypeEntity,
    GroupEntity,
    LabelEntity,
    LabelEntityPk,
    RelationEntity,
    RelationType,
    Reviewer,
)


class ILabelRepository(ABC):
    @abstractmethod
    def add(self, label_entity: LabelEntity) -> LabelEntity:
        pass

    @abstractmethod
    def get_list(self, options: LabelListFilterObject) -> List[LabelEntity]:
        pass

    @abstractmethod
    def add_label_to_organisation(self, label_entity_pk: LabelEntityPk, organisation_name: str) -> None:
        pass

    @abstractmethod
    def get_organisation_label_entity_pks(
        self,
        organisation_name: str,
        options: LabelListFilterObject,
    ) -> List[LabelEntityPk]:
        pass


class ICommentRepository(ABC):
    @abstractmethod
    def add(self, comment_entity: CommentEntity, document_entity_pk: DocumentEntityPk) -> CommentEntity:
        pass


class IDocumentEntityRepository(ABC):  # pylint: disable=too-many-public-methods
    @abstractmethod
    def get(self, pk: DocumentEntityPk) -> DocumentEntity:
        pass

    @abstractmethod
    def find_by_pks(self, document_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get_main_info_by_pks(self, document_pks: list[DocumentEntityPk]) -> list[dict]:
        pass

    @abstractmethod
    def add(self, entity: DocumentEntity) -> DocumentEntity:
        pass

    @abstractmethod
    def delete(self, entity: DocumentEntity) -> bool:
        pass

    @abstractmethod
    def update(self, entity: DocumentEntity) -> DocumentEntity:
        pass

    @abstractmethod
    def batch_update(self, document_entities: List[DocumentEntity]) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get_list_by_filter(self, filtering: DocumentListFilterObject) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get_total_count_by_filter(self, filtering: DocumentListFilterObject) -> int:
        pass

    @abstractmethod
    def clear_error(self, pk: DocumentEntityPk) -> bool:
        pass

    @abstractmethod
    def update_state(self, pk: DocumentEntityPk, state: DocumentStateEnum) -> bool:
        pass

    @abstractmethod
    def add_label(self, label_pk: LabelEntityPk, document_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:
        pass

    @abstractmethod
    def remove_label(self, label_pk: LabelEntityPk, pk: DocumentEntityPk) -> bool:
        pass

    @abstractmethod
    def add_bulk_labels(self, label_pks: list[LabelEntityPk], document_pk: DocumentEntityPk) -> list[LabelEntityPk]:
        pass

    @abstractmethod
    def get_document_metadata(self, document_pk: DocumentEntityPk) -> DocumentMetadata:
        pass

    @abstractmethod
    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        pass

    @abstractmethod
    def delete_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        pass

    @abstractmethod
    def get_document_count_of_type(self, document_type_code: str) -> int:
        pass

    @abstractmethod
    def find_by_document_type_code(self, document_type_code: str) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def check_documents_for_organisation(
        self,
        organisation_entity_name: str,
        document_ids: list[DocumentEntityPk],
    ) -> bool:
        pass

    @abstractmethod
    def get_descendants(self, pk: DocumentEntityPk, include_containers: bool = False) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def get_assigned_relation(self, pk: DocumentEntityPk) -> List[RelationEntity]:
        pass

    @abstractmethod
    def add_document_to_user(self, document_entity_pk: DocumentEntityPk, user_entity_pk: str) -> None:
        pass

    @abstractmethod
    def get_user_document_entity_pks(self, user_entity_pk: str) -> List[DocumentEntityPk]:
        pass

    @abstractmethod
    def add_document_to_user_and_organisation(
        self,
        document_entity_pk: DocumentEntityPk,
        user_entity_pk: str,
        organisation_entity_pk: str,
    ) -> None:
        pass

    @abstractmethod
    def get_organisation_document_entity_pks(self, organisation_entity_pk: str) -> List[DocumentEntityPk]:
        pass

    @abstractmethod
    def select_for_update(self, document_pks: List[DocumentEntityPk]):
        pass


class IDocumentLogRepository(ABC):
    @abstractmethod
    def add(self, entity: DocumentLogEntity) -> DocumentLogEntity:
        pass


class IAnalyticsRepository(ABC):
    @abstractmethod
    def get_document_type_changes(self, filters: DocumentTypeChangeFilter) -> List[DocumentTypeChangeAggregation]:
        pass


class IBatchUploadDataRepository(ABC):
    @abstractmethod
    def create_batch_id(self) -> str:
        pass

    @abstractmethod
    def exists_batch_id(self, batch_id: str) -> bool:
        pass

    @abstractmethod
    def get_batch_upload_data(self, batch_id: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def update_batch_upload_data(self, batch_id: str, upload_data: Dict[str, str]) -> None:
        pass


class IRelationRepository(ABC):
    @abstractmethod
    def get_relation(self, relation: RelationEntity) -> RelationEntity:
        pass

    @abstractmethod
    def get_relation_list(self, relation_filter: RelationFilterObject = RelationFilterObject()) -> List[RelationEntity]:
        pass

    @abstractmethod
    def get_relation_type_list(self) -> List[RelationType]:
        pass

    @abstractmethod
    def get_children_list(self, relation: RelationEntity) -> List[RelationEntity]:
        pass

    @abstractmethod
    def get_assigned_documents(self, relation: RelationEntity) -> List[int]:
        pass

    @abstractmethod
    def create_relation(self, relation: RelationEntity) -> RelationEntity:
        pass

    @abstractmethod
    def create_relation_type(self, relation_type: str) -> None:
        pass

    @abstractmethod
    def assign_document(self, relation: RelationEntity) -> None:
        pass

    @abstractmethod
    def update(self, relation: RelationEntity, relation_update_info: UpdateRelationEntity) -> RelationEntity:
        pass

    @abstractmethod
    def update_relation_type(self, relation_type: str, type_update_info: RelationType) -> RelationType:
        pass

    @abstractmethod
    def delete_relation(
        self,
        relation: RelationEntity,
    ) -> bool:
        pass

    @abstractmethod
    def delete_assigned_documents(
        self,
        relation: RelationEntity,
    ) -> bool:
        pass


class IDocumentTypeRepository(ABC):
    @abstractmethod
    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentTypeEntity:
        pass

    @abstractmethod
    def save(self, document_type: DocumentTypeEntity) -> None:
        pass

    @abstractmethod
    def save_all(self, document_types: list[DocumentTypeEntity]) -> None:
        pass

    @abstractmethod
    def delete(self, document_type: DocumentTypeEntity) -> None:
        pass


class IGroupRepository(ABC):
    @abstractmethod
    def find_by_id_for_tenant(self, group_id: str, tenant_id: str) -> GroupEntity:
        pass

    @abstractmethod
    def save(self, group_id: str, tenant_id: str, name: str) -> None:
        pass

    @abstractmethod
    def save_all(self, groups: list[GroupInfo]) -> None:
        pass

    @abstractmethod
    def mark_deleted(self, group_id: str, tenant_id: str) -> None:
        pass
