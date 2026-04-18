import random
from uuid import uuid4

import pytest

from deps_documents.domain.entities import ParsingFeature
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository, FakeGroupRepository


@pytest.mark.application
def test_create_document_with_existing_file(application, uow):
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    group_id = uuid4().hex
    blob_name = uuid4().hex
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    assign_to_me = True
    parsing_features = {ParsingFeature.TEXT}
    metadata = {"field": "value"}
    parent_id = uuid4().hex
    needs_unification = True
    needs_extraction = True

    fake_document_db = {}
    uow.document = FakeDocumentRepository(fake_document_db)
    uow.group = FakeGroupRepository()
    uow.group.save(group_id=group_id, tenant_id=tenant_id, name=uuid4().hex)

    test_document = application.document_v3().create_document_with_existing_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group_id,
        blob_name=blob_name,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        parent_id=parent_id,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
    )

    assert test_document.title == document_name
    assert test_document.document_type == document_type_id
    assert test_document.group.id == group_id
    assert test_document.language == language
    assert test_document.engine == engine
    assert test_document.files[0].blob_name == blob_name
    assert test_document.parent_id == parent_id
    assert test_document.llm_type == llm_type
    assert test_document.parsing_features == parsing_features
    assert test_document.needs_unification == needs_unification
    assert test_document.needs_extraction == needs_extraction

    if not assign_to_me:
        assert test_document.reviewer is not None
    else:
        assert test_document.reviewer is None


@pytest.mark.application
def test_create_document_with_existing_file__no_document_type(application, uow):
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = None
    group_id = uuid4().hex
    blob_name = uuid4().hex
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    assign_to_me = True
    parsing_features = {ParsingFeature.TEXT}
    metadata = {"field": "value"}
    parent_id = uuid4().hex
    needs_unification = True
    needs_extraction = True

    fake_db = {}
    uow.document = FakeDocumentRepository(fake_db)

    test_document = application.document_v3().create_document_with_existing_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group_id,
        blob_name=blob_name,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        parent_id=parent_id,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
    )

    assert test_document.document_type == document_type_id


@pytest.mark.application
def test_create_document(application, uow, blob_storage_mock):
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    group_id = uuid4().hex
    file_name = "a.png"
    file_content = b"qwerty"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    assign_to_me = True
    parsing_features = {ParsingFeature.TEXT}
    metadata = {"field": "value"}
    parent_id = uuid4().hex
    needs_unification = True
    needs_extraction = True

    fake_db = {}
    uow.document = FakeDocumentRepository(fake_db)

    test_document = application.document_v3().create_document(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group_id,
        file_name=file_name,
        file_content=file_content,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        parent_id=parent_id,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
    )

    assert test_document.document_type == document_type_id
    assert len(test_document.files) == 1


@pytest.mark.application
def test_create_document__no_document_type(application, uow, blob_storage_mock):
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = None
    group_id = uuid4().hex
    file_name = "b.png"
    file_content = b"abcd"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    assign_to_me = True
    parsing_features = {ParsingFeature.TEXT}
    metadata = {"field": "value"}
    parent_id = uuid4().hex
    needs_unification = True
    needs_extraction = True

    fake_db = {}
    uow.document = FakeDocumentRepository(fake_db)

    test_document = application.document_v3().create_document(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group_id,
        file_name=file_name,
        file_content=file_content,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        parent_id=parent_id,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
    )

    assert test_document.document_type == document_type_id
