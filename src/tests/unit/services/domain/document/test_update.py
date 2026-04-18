from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.events.events import DocumentProcessed
from tests.factories import DocumentEntityFactory


def test_document_update__completed__document_processed_event_added():
    document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.DATA_EXTRACTION)
    updated_document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED)

    document.update(updated_document)

    assert document.state == DocumentStateEnum.COMPLETED
    assert isinstance(document.events[0], DocumentProcessed)
