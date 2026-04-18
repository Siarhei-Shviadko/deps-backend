import random
from uuid import uuid4

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


@pytest.mark.application
def test_create_document(application, uow):
    document_name, document_type, language, engine, blob_name, tenant, llm_type = (
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
    )

    fake_db = {}
    uow.document = FakeDocumentRepository(fake_db)

    test_document_id = application.document().create_document(
        document_name=document_name,
        document_type=document_type,
        language=language,
        engine=engine,
        blob_name=blob_name,
        tenant=tenant,
        llm_type=llm_type,
    )
    test_output = fake_db[test_document_id]

    assert test_output.title == document_name
    assert test_output.document_type == document_type
    assert test_output.language == language
    assert test_output.engine == engine
    assert test_output.files[0].blob_name == blob_name


@pytest.mark.application
def test_create_document_with_parent_id(application, uow):
    document_name, document_type, language, engine, blob_name, tenant, parent_id, llm_type = (
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        uuid4().hex,
        str(random.randint(1, 100)),
        uuid4().hex,
    )

    fake_db = {}
    uow.document = FakeDocumentRepository(fake_db)

    test_document_id = application.document().create_document(
        document_name=document_name,
        document_type=document_type,
        language=language,
        engine=engine,
        blob_name=blob_name,
        tenant=tenant,
        parent_id=parent_id,
        llm_type=llm_type,
    )
    test_output = fake_db[test_document_id]

    assert test_output.title == document_name
    assert test_output.document_type == document_type
    assert test_output.language == language
    assert test_output.engine == engine
    assert test_output.files[0].blob_name == blob_name
    assert test_output.parent_id == parent_id
