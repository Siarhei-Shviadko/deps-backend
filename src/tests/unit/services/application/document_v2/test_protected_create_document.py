import random
from uuid import uuid4

import pytest


@pytest.mark.application
def test_protected_create_document(application, document_service_mock, document_access_manager_mock):
    document_id, document_name, document_type, language, engine, blob_name, tenant, llm_type = (
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
    )

    document_service_mock.create_document.return_value = document_id
    test_document_id = application.document_access().create_document(
        document_name=document_name,
        document_type=document_type,
        language=language,
        engine=engine,
        blob_name=blob_name,
        tenant=tenant,
        llm_type=llm_type,
    )

    assert test_document_id == document_id
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)


@pytest.mark.application
def test_protected_create_document_with_parent_id(application, document_service_mock, document_access_manager_mock):
    document_id, document_name, document_type, language, engine, blob_name, tenant, parent_id, llm_type = (
        str(random.randint(1, 100)),
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        str(random.randint(1, 100)),
        uuid4().hex,
    )

    document_service_mock.create_document.return_value = document_id
    test_document_id = application.document_access().create_document(
        document_name=document_name,
        document_type=document_type,
        language=language,
        engine=engine,
        blob_name=blob_name,
        tenant=tenant,
        llm_type=llm_type,
        parent_id=parent_id,
    )

    assert test_document_id == document_id
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)
