from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_documents.application import GroupService
from deps_documents.domain.events import (
    GetGroupsReply,
    GroupCreated,
    GroupDeleted,
    GroupInfoUpdated,
)
from deps_documents.events_handler.handlers import (
    get_groups_reply_handler,
    group_created_handler,
    group_deleted_handler,
    group_info_updated_handler,
)


def test_get_groups_reply_handler(
    group_service_mock: GroupService,
    get_groups_reply_command: CommandMessage[GetGroupsReply],
):
    group_service_mock.save_groups.return_value = None

    get_groups_reply_handler(get_groups_reply_command)

    group_service_mock.save_groups.assert_called_once_with(
        get_groups_reply_command.command.groups,
    )


def test_group_created_handler(
    group_service_mock: GroupService,
    group_created_envelope: DomainEventEnvelope[GroupCreated],
):
    group_service_mock.save_group.return_value = None

    group_created_handler(group_created_envelope)

    group_service_mock.save_group.assert_called_once_with(
        group_id=group_created_envelope.event.id,
        tenant_id=group_created_envelope.event.tenant_id,
        name=group_created_envelope.event.name,
    )


def test_group_deleted_handler(
    group_service_mock: GroupService,
    group_deleted_envelope: DomainEventEnvelope[GroupDeleted],
):
    group_service_mock.save_group.return_value = None

    group_deleted_handler(group_deleted_envelope)

    group_service_mock.mark_deleted.assert_called_once_with(
        group_id=group_deleted_envelope.event.id,
        tenant_id=group_deleted_envelope.event.tenant_id,
    )


def test_group_info_updated_handler(
    group_service_mock: GroupService,
    group_info_updated_envelope: DomainEventEnvelope[GroupInfoUpdated],
):
    group_service_mock.save_group.return_value = None

    group_info_updated_handler(group_info_updated_envelope)

    group_service_mock.save_group.assert_called_once_with(
        group_id=group_info_updated_envelope.event.id,
        tenant_id=group_info_updated_envelope.event.tenant_id,
        name=group_info_updated_envelope.event.name,
    )
