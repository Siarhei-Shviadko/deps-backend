from uuid import uuid4

import pytest

from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


@pytest.mark.application
def test_assign_document_type(application, uow):
    document_id = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    document = DocumentEntityFactory(pk=document_id, document_type=None)

    fake_db = {document_id: document}
    uow.document = FakeDocumentRepository(fake_db)

    application.document_v3().assign_document_type(
        tenant_id=tenant_id,
        document_id=document_id,
        document_type_id=document_type_id,
    )

    assert fake_db[document_id].document_type == document_type_id
