from uuid import uuid4

import pytest

from deps_documents.domain.entities import ParsingFeature
from tests.factories import DocumentEntityFactory


@pytest.mark.application
def test_protected_create_document_with_existing_file(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    assign_to_me = True

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
    )

    document_service_v3_mock.create_document_with_existing_file.return_value = document

    test_document_id = application.document_access_v3().create_document_with_existing_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=document.group_id,
        blob_name=document.blob_names[0],
        engine=document.engine,
        language=document.language,
        llm_type=document.llm_type,
        assign_to_me=assign_to_me,
    )

    assert test_document_id == document_id
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)


@pytest.mark.application
def test_protected_create_document(application, document_service_v3_mock, document_access_manager_mock):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    file_content = b"qwerty"
    assign_to_me = True

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
    )

    document_service_v3_mock.create_document.return_value = document

    test_document_id = application.document_access_v3().create_document(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=document.group_id,
        file_name=document.blob_names[0],
        file_content=file_content,
        engine=document.engine,
        language=document.language,
        llm_type=document.llm_type,
        assign_to_me=assign_to_me,
    )

    assert test_document_id == document_id
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)
