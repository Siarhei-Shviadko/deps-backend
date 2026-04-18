import uuid

import pytest

from deps_documents.application import GroupService
from deps_documents.domain.exceptions import NotFoundError
from tests.factories import GroupEntityFactory


@pytest.mark.application
def test_save_and_find_group__success(uow, group_service: GroupService, tenant_id: str):
    group = GroupEntityFactory()

    group_service.save_group(group_id=group.id, tenant_id=tenant_id, name=group.name)

    uow.group.find_by_id_for_tenant(group_id=group.id, tenant_id=tenant_id)


@pytest.mark.application
def test_save_groups__success(uow, group_service: GroupService, tenant_id: str):
    groups = [
        {
            "id": group.id,
            "tenant_id": tenant_id,
            "name": group.name,
            "is_deleted": False,
        }
        for group in GroupEntityFactory.create_batch(3)
    ]

    group_service.save_groups(groups)

    for group in groups:
        uow.group.find_by_id_for_tenant(group["id"], group["tenant_id"])


@pytest.mark.application
def test_group_find_by_id_for_tenant__not_found(uow, group_service: GroupService, tenant_id: str):
    with pytest.raises(NotFoundError):
        group_service.find_by_id_for_tenant(uuid.uuid4().hex, uuid.uuid4().hex)


@pytest.mark.application
def test_group_mark_deleted__success(uow, group_service: GroupService, tenant_id: str):
    group = GroupEntityFactory()
    group_service.save_group(group_id=group.id, tenant_id=tenant_id, name=group.name)

    uow.group.find_by_id_for_tenant(group_id=group.id, tenant_id=tenant_id)

    group_service.mark_deleted(group_id=group.id, tenant_id=tenant_id)

    with pytest.raises(NotFoundError):
        uow.group.find_by_id_for_tenant(group_id=group.id, tenant_id=tenant_id)
