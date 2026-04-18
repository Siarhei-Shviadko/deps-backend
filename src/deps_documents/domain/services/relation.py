from typing import Callable

from deps_documents.domain.dtos import (
    DocumentListDataObject,
    ListResponseMetaDataObject,
    RelationDataObject,
    RelationFilterObject,
    RelationTypeDataObject,
    UpdateRelationEntity,
)
from deps_documents.domain.entities import RelationEntity, RelationType
from deps_documents.domain.exceptions import DocumentAssigningError
from deps_documents.domain.interfaces import IDocumentUnitOfWork
from deps_documents.domain.services.document import DocumentService
from deps_documents.infrastructure.repositories.helpers import cast_from_db_pk


class RelationService:
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork], document_service: DocumentService):
        self._uow = uow
        self.document_service = document_service

    def get_relation(self, relation: RelationEntity) -> RelationEntity:
        with self._uow() as uow:
            relation = uow.relation.get_relation(relation)
            uow.commit()
        return relation

    def get_relation_list(self, relation: RelationFilterObject = RelationFilterObject()) -> RelationDataObject:
        with self._uow() as uow:
            relation_list = uow.relation.get_relation_list(relation)
            uow.commit()
        return RelationDataObject(
            meta=ListResponseMetaDataObject(total=len(relation_list), size=len(relation_list)),
            content=relation_list,
        )

    def get_children_list(self, relation) -> RelationDataObject:
        with self._uow() as uow:
            children_list = uow.relation.get_children_list(relation)
            uow.commit()

        return RelationDataObject(
            meta=ListResponseMetaDataObject(total=len(children_list), size=len(children_list)),
            content=children_list,
        )

    def get_relation_type_list(self) -> RelationTypeDataObject:
        with self._uow() as uow:
            relation_type_list = uow.relation.get_relation_type_list()
            uow.commit()
        return RelationTypeDataObject(
            meta=ListResponseMetaDataObject(total=len(relation_type_list), size=len(relation_type_list)),
            content=relation_type_list,
        )

    def get_document(self, relation: RelationEntity) -> DocumentListDataObject:
        with self._uow() as uow:
            relation = uow.relation.get_relation(relation)
            documents = [self.document_service.get(cast_from_db_pk(doc_id)) for doc_id in relation.assigned_documents]
            uow.commit()
        return DocumentListDataObject(
            content=documents,
            meta=ListResponseMetaDataObject(total=len(documents), size=len(documents)),
        )

    def assign_document(self, relation: RelationEntity) -> None:
        with self._uow() as uow:
            uow.relation.assign_document(relation)
            uow.commit()

    def create_relation(self, relation: RelationEntity) -> RelationEntity:
        with self._uow() as uow:
            created_relation = uow.relation.create_relation(relation)

            if relation.assigned_documents is not None:
                try:
                    self.assign_document(relation)
                    created_relation.assigned_documents = relation.assigned_documents
                except DocumentAssigningError:
                    self.delete_relation(relation)
                    uow.commit()
                    raise
            uow.commit()
        return relation

    def create_relation_type(self, relation_type: str) -> None:
        with self._uow() as uow:
            uow.relation.create_relation_type(relation_type)
            uow.commit()

    def update(self, relation: RelationEntity, relation_update_info: UpdateRelationEntity) -> RelationEntity:
        with self._uow() as uow:
            updated = uow.relation.update(relation=relation, relation_update_info=relation_update_info)
            uow.commit()
        return updated

    def update_relation_type(self, relation_type: str, type_update_info: RelationType) -> RelationType:
        with self._uow() as uow:
            updated = uow.relation.update_relation_type(
                relation_type=relation_type,
                type_update_info=type_update_info,
            )
            uow.commit()
        return updated

    def delete_relation(self, relation: RelationEntity) -> bool:
        with self._uow() as uow:
            deleted = uow.relation.delete_relation(relation)
            uow.commit()
        return deleted

    def delete_assigned_documents(self, relation: RelationEntity) -> bool:
        with self._uow() as uow:
            deleted = uow.relation.delete_assigned_documents(relation)
            uow.commit()
        return deleted
