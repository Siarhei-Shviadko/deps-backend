from uuid import uuid4

from deps_message_flow.commands.common import CommandReplyOutcome
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_documents.domain.events import (
    GetGroupsReply,
    GroupCreated,
    GroupDeleted,
    GroupInfoUpdated,
)

from .save_batch_documents_fixtures import *


@pytest.fixture()
def get_groups_reply_command(mocker, tenant_id: str) -> CommandMessage[GetGroupsReply]:
    cm = mocker.Mock(CommandMessage)
    cm.command.groups = [{"id": uuid4().hex, "tenant_id": tenant_id, "name": uuid4().hex, "is_deleted": False}]
    cm.message.get_required_header.return_value = CommandReplyOutcome.SUCCESS.name

    return cm


@pytest.fixture()
def group_created_envelope(mocker, tenant_id: str) -> DomainEventEnvelope[GroupCreated]:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex
    dee.event.tenant_id = tenant_id
    dee.event.name = uuid4().hex

    return dee


@pytest.fixture()
def group_deleted_envelope(mocker, tenant_id: str) -> DomainEventEnvelope[GroupDeleted]:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex
    dee.event.tenant_id = tenant_id

    return dee


@pytest.fixture()
def group_info_updated_envelope(mocker, tenant_id: str) -> DomainEventEnvelope[GroupInfoUpdated]:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex
    dee.event.tenant_id = tenant_id
    dee.event.name = uuid4().hex

    return dee
