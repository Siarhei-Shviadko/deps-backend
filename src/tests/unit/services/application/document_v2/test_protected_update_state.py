from uuid import uuid4

import pytest


@pytest.mark.application
def test_protected_update_state(application, document_service_mock, document_access_manager_mock):
    test_document_id = uuid4().hex

    application.document_access().update_state(test_document_id, "some_state", None, None)

    document_access_manager_mock.check_is_accessible_write.assert_called_with([test_document_id])
