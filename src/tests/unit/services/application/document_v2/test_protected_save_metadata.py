import random

import pytest


@pytest.mark.application
def test_protected_save_metadata(application, document_service_mock, document_access_manager_mock):
    document_id = random.randint(1, 100)
    document_metadata = {"extension": "jpeg"}

    application.document_access().save_metadata(document_id, document_metadata)

    document_access_manager_mock.check_is_accessible_write.assert_called_with([document_id])
