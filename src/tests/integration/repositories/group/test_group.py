from typing import Any
from uuid import uuid4

import pytest

from deps_documents.domain.entities import GroupEntity
from deps_documents.domain.exceptions import NotFoundError
from tests.factories import GroupEntityFactory


def _build_group_info(group: GroupEntity, tenant_id: str) -> dict[str, Any]:
    return {
        "id": group.id,
        "tenant_id": tenant_id,
        "name": group.name,
        "is_deleted": False,
    }


def test_save_and_find_group__success(uow, tenant_id: str):
    group = GroupEntityFactory()

    uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)
    saved_group = uow.group.find_by_id_for_tenant(group_id=group.id, tenant_id=tenant_id)

    assert group == saved_group


def test_group_find_by_id_for_tenant__not_found(uow):
    with pytest.raises(NotFoundError):
        uow.group.find_by_id_for_tenant(uuid4().hex, uuid4().hex)


def test_save_groups__success(uow, tenant_id: str):
    groups = [_build_group_info(group=group, tenant_id=tenant_id) for group in GroupEntityFactory.create_batch(3)]
    uow.group.save_all(groups)

    for group in groups:
        uow.group.find_by_id_for_tenant(group["id"], tenant_id)


def test_group_mark_deleted__success(uow, tenant_id: str):
    group = GroupEntityFactory()

    uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)

    uow.group.find_by_id_for_tenant(group_id=group.id, tenant_id=tenant_id)

    uow.group.mark_deleted(group_id=group.id, tenant_id=tenant_id)

    with pytest.raises(NotFoundError):
        uow.group.find_by_id_for_tenant(uuid4().hex, uuid4().hex)
