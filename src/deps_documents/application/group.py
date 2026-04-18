import logging
from typing import Callable

from deps_message_flow.commands.producer import CommandProducer

from deps_documents.constants import (
    DOCUMENT_COMMANDS_CHANNEL,
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
)
from deps_documents.domain.dtos import GroupInfo
from deps_documents.domain.entities import GroupEntity
from deps_documents.domain.events import GetGroups
from deps_documents.domain.interfaces import IDocumentUnitOfWork

__all__ = ["GroupService"]


class GroupService:
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork], command_producer: CommandProducer):
        self._uow = uow
        self._command_producer = command_producer
        self._logger = logging.getLogger(self.__class__.__name__)

    def initialize(self) -> None:
        self._command_producer.send(
            DOCUMENT_COMMANDS_CHANNEL,
            GetGroups(),
            DOCUMENT_COMMANDS_REPLIES_CHANNEL,
        )
        self._logger.info("Command GetGroups sent")

    def find_by_id_for_tenant(self, group_id: str, tenant_id: str) -> GroupEntity:
        with self._uow() as uow:
            return uow.group.find_by_id_for_tenant(group_id=group_id, tenant_id=tenant_id)

    def save_group(self, group_id: str, tenant_id: str, name: str) -> None:
        with self._uow() as uow:
            uow.group.save(group_id=group_id, tenant_id=tenant_id, name=name)

            uow.commit()

    def save_groups(self, group_infos: list[GroupInfo]) -> None:
        with self._uow() as uow:
            uow.group.save_all(group_infos)

            uow.commit()

    def mark_deleted(self, group_id: str, tenant_id: str) -> None:
        with self._uow() as uow:
            uow.group.mark_deleted(group_id=group_id, tenant_id=tenant_id)
            uow.commit()
