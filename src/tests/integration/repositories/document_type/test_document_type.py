from uuid import uuid4

import pytest

from deps_documents.domain.entities import DocumentTypeEntity
from deps_documents.domain.exceptions import NotFoundError


def build_document_type() -> DocumentTypeEntity:
    return DocumentTypeEntity(
        id=str(uuid4()),
        tenant=str(uuid4()),
        name=str(uuid4()),
    )


def test_save_document_type__success(uow):
    document_type = build_document_type()
    uow.document_type.save(document_type)
    uow.document_type.find_by_id_for_tenant(document_type.id, document_type.tenant)


def test_save_document_types__success(uow):
    document_types = [build_document_type() for _ in range(3)]
    uow.document_type.save_all(document_types)

    for document_type in document_types:
        uow.document_type.find_by_id_for_tenant(document_type.id, document_type.tenant)


@pytest.mark.application
def test_find_by_id_for_tenant__success(uow):
    document_type = build_document_type()
    uow.document_type.save(document_type)

    uow.document_type.find_by_id_for_tenant(document_type.id, document_type.tenant)


@pytest.mark.application
def test_find_by_id_for_tenant__not_found(uow):
    document_type = build_document_type()
    with pytest.raises(NotFoundError):
        uow.document_type.find_by_id_for_tenant(document_type.id, document_type.tenant)


@pytest.mark.application
def test_delete_document_type__success(uow):
    document_type = build_document_type()
    uow.document_type.save(document_type)
    uow.document_type.delete(document_type)

    with pytest.raises(NotFoundError):
        uow.document_type.find_by_id_for_tenant(document_type.id, document_type.tenant)
