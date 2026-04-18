import random

import pytest

from tests.fakes import FakeDocumentMetadataRepository


@pytest.mark.application
def test_save_metadata(application, uow):
    document_id = random.randint(1, 100)
    document_metadata = {"extension": "jpeg"}
    fake_db = {}
    uow.document = FakeDocumentMetadataRepository(fake_db)

    application.document().save_metadata(document_id, document_metadata)
    saved_metadata = fake_db[document_id]

    assert saved_metadata == document_metadata
