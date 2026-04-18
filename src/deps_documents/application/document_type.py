import logging
from typing import Any, Callable

from deps_message_flow.commands.producer import CommandProducer

from deps_documents.constants import (
    DOCUMENT_COMMANDS_CHANNEL,
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
)
from deps_documents.domain.entities import DocumentTypeEntity
from deps_documents.domain.events import GetDocumentTypes
from deps_documents.domain.interfaces import IDocumentUnitOfWork

__all__ = ["DocumentTypeService"]


class DocumentTypeService:
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork], command_producer: CommandProducer):
        self._uow = uow
        self._command_producer = command_producer
        self._logger = logging.getLogger(self.__class__.__name__)

    def initialize(self) -> None:
        self._command_producer.send(
            DOCUMENT_COMMANDS_CHANNEL,
            GetDocumentTypes(),
            DOCUMENT_COMMANDS_REPLIES_CHANNEL,
        )
        self._logger.info("Command GetDocumentTypes sent")

    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentTypeEntity:
        with self._uow() as uow:
            return uow.document_type.find_by_id_for_tenant(
                document_type_id=document_type_id,
                tenant_id=tenant_id,
            )

    def save_document_type(self, document_type_id: str, tenant_id: str, name: str) -> None:
        document_type = DocumentTypeEntity(id=document_type_id, tenant=tenant_id, name=name)

        with self._uow() as uow:
            uow.document_type.save(document_type)
            uow.commit()

    def save_document_types(self, document_types: list[dict[str, Any]]) -> None:
        doc_types_entities = []
        for doc_type in document_types:
            document_type = DocumentTypeEntity(
                id=doc_type["document_type"],
                tenant=doc_type["tenant"],
                name=doc_type["name"],
            )
            doc_types_entities.append(document_type)

        with self._uow() as uow:
            uow.document_type.save_all(doc_types_entities)
            uow.commit()

    def delete_document_type(self, document_type_id: str, tenant_id: str) -> None:
        with self._uow() as uow:
            document_type = uow.document_type.find_by_id_for_tenant(
                document_type_id=document_type_id,
                tenant_id=tenant_id,
            )

            uow.document_type.delete(document_type)
            uow.commit()
