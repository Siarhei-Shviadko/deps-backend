from unittest.mock import call
from uuid import uuid4

import pytest

from deps_documents.domain.constants import (
    DocumentProcessingResult,
    DocumentStateEnum,
    ErrorType,
)
from deps_documents.domain.entities import DocumentEntityPk, DocumentMetadata
from deps_documents.domain.events.events import (
    DocumentProcessed,
    DocumentStateUpdated,
    DocumentTypeAssignedToDocument,
)
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


@pytest.mark.application
def test_update_state(application, uow):
    test_document_id = uuid4().hex
    test_document = DocumentEntityFactory(pk=test_document_id, state=DocumentStateEnum.NEW)
    state = DocumentStateEnum.PREPROCESSING

    fake_db = {test_document_id: test_document}
    uow.document = FakeDocumentRepository(fake_db)

    application.document().update_state(test_document_id, state, None, None)
    test_output = fake_db[test_document_id]

    assert test_output.state == state
    assert test_output.error is None


@pytest.mark.application
def test_update_state_to_failed(application, uow):
    test_document_id = uuid4().hex
    initial_state = DocumentStateEnum.NEW
    test_document = DocumentEntityFactory(pk=test_document_id, state=initial_state)
    state = DocumentStateEnum.FAILED

    fake_db = {test_document_id: test_document}
    uow.document = FakeDocumentRepository(fake_db)

    application.document().update_state(test_document_id, state, ErrorType.SYSTEM, "some error message")
    test_output = fake_db[test_document_id]

    assert test_output.state == state
    assert test_output.error is not None
    assert test_output.error.description == "system: some error message"
    assert test_output.error.in_state == initial_state


@pytest.mark.application
def test_update_state__event_sent(application, uow, faker):
    test_document_id = DocumentEntityPk(uuid4().hex)
    test_document = DocumentEntityFactory(pk=test_document_id, state=DocumentStateEnum.NEW)
    new_state = DocumentStateEnum.FAILED
    error_message = faker.sentence()
    metadata = {faker.word(): faker.word()}
    uow.document = FakeDocumentRepository({test_document_id: test_document})
    uow.document.upsert_document_metadata(DocumentMetadata(document_id=test_document_id, metadata=metadata))

    application.document().update_state(test_document_id, new_state, ErrorType.BUSINESS, error_message)

    uow.add_events.assert_called_once_with(
        [
            DocumentStateUpdated(
                document_id=test_document_id,
                state=new_state.value,
                metadata=metadata,
                error_in_state=test_document.error.in_state if test_document.error else None,
            ),
            DocumentProcessed(
                document_id=test_document_id,
                document_type_code=test_document.document_type,
                processing_result=DocumentProcessingResult.FAILED,
                error_message=error_message,
            ),
        ],
    )


@pytest.mark.application
def test_assigned_to_document__event_sent(application, uow, faker):
    test_document_id = DocumentEntityPk(uuid4().hex)
    test_document_type_id = uuid4().hex
    test_tenant_id = uuid4().hex
    test_metadata = {faker.word(): faker.word()}
    test_document = DocumentEntityFactory(pk=test_document_id, document_type=None)
    uow.document = FakeDocumentRepository({test_document_id: test_document})
    uow.document.upsert_document_metadata(DocumentMetadata(document_id=test_document_id, metadata=test_metadata))

    application.document_v3().assign_document_type(
        tenant_id=test_tenant_id,
        document_id=test_document_id,
        document_type_id=test_document_type_id,
    )

    uow.add_events.assert_has_calls(
        [
            call(
                [
                    DocumentTypeAssignedToDocument(
                        document_id=test_document_id,
                        document_type_id=test_document_type_id,
                        metadata=test_metadata,
                    ),
                ]
            ),
        ]
    )
