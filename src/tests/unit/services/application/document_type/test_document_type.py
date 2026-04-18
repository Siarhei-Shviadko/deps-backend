import uuid

import pytest

from deps_documents.domain.exceptions import NotFoundError
from tests.fakes import FakeDocumentTypeRepository


@pytest.mark.application
def test_save_document_type__success(uow, document_type_service, test_document_type):
    document_type_service.save_document_type(test_document_type.id, test_document_type.tenant, test_document_type.name)

    uow.document_type.find_by_id_for_tenant(test_document_type.id, test_document_type.tenant)


@pytest.mark.application
def test_save_document_types__success(uow, document_type_service):
    document_types = [
        {
            "document_type": str(uuid.uuid4()),
            "tenant": str(uuid.uuid4()),
            "name": str(uuid.uuid4()),
        }
        for _ in range(5)
    ]

    document_type_service.save_document_types(document_types)

    for document_type in document_types:
        uow.document_type.find_by_id_for_tenant(document_type["document_type"], document_type["tenant"])


@pytest.mark.application
def test_find_by_id_for_tenant__success(uow, document_type_service, test_document_type):
    document_type_service.save_document_type(test_document_type.id, test_document_type.tenant, test_document_type.name)

    document_type_service.find_by_id_for_tenant(test_document_type.id, test_document_type.tenant)


@pytest.mark.application
def test_find_by_id_for_tenant__not_found(uow, document_type_service, test_document_type):
    with pytest.raises(NotFoundError):
        document_type_service.find_by_id_for_tenant(test_document_type.id, test_document_type.tenant)


@pytest.mark.application
def test_delete_document_type__success(uow, document_type_service, test_document_type):
    document_type_service.save_document_type(test_document_type.id, test_document_type.tenant, test_document_type.name)
    document_type_service.find_by_id_for_tenant(test_document_type.id, test_document_type.tenant)

    document_type_service.delete_document_type(test_document_type.id, test_document_type.tenant)

    with pytest.raises(NotFoundError):
        document_type_service.find_by_id_for_tenant(test_document_type.id, test_document_type.tenant)
