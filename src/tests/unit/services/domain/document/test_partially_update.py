from random import choice
from uuid import uuid4

from deps_documents.domain.constants import END_STATES
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.events import DocumentFieldsUpdated, DocumentStateUpdated
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


def test_partially_update__state_updated__event_sent(uow, domain_services):
    field = "state"
    field_value = choice(END_STATES)
    document_pk = DocumentEntityPk(uuid4().hex)
    document = DocumentEntityFactory(pk=document_pk)
    uow.document = FakeDocumentRepository({document_pk: document})

    domain_services.document().partially_update(document_pk, {field: field_value})

    uow.add_events.assert_called_once_with(
        [
            DocumentFieldsUpdated(document_id=document_pk, document_metadata={}, updates={"state": field_value}),
            DocumentStateUpdated(
                document_id=document_pk,
                state=field_value,
                metadata={},
                error_in_state=document.error.in_state if document.error else None,
            ),
        ],
    )
