from uuid import uuid4

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import Reviewer
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


@pytest.mark.application
def test_unassign_reviewer(application, uow):
    document_service = application.document()
    uow.document = FakeDocumentRepository(dict())
    document_name, document_type, language, engine, blob_name, tenant, llm_type = (
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
    )

    document_id = document_service.create_document(
        document_name=document_name,
        document_type=document_type,
        language=language,
        engine=engine,
        blob_name=blob_name,
        tenant=tenant,
        reviewer=Reviewer(id=uuid4().hex),
        llm_type=llm_type,
    )
    document_service.unassign_reviewer(document_id)
    document = uow.document.get(document_id)

    assert document.reviewer is None
