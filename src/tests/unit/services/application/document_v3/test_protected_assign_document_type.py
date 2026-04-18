from uuid import uuid4

import pytest


@pytest.mark.application
def test_protected_assign_document_type(application, document_service_v3_mock, document_access_manager_mock):
    document_id = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex

    document_service_v3_mock.create_document_with_existing_file.return_value = None

    application.document_access_v3().assign_document_type(
        tenant_id=tenant_id,
        document_id=document_id,
        document_type_id=document_type_id,
    )

    document_access_manager_mock.check_is_accessible_write.assert_called_with(document_entity_pks=[document_id])
