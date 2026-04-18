from uuid import uuid4

from deps_message_flow.events.common import DomainEvent

from deps_documents.application.document import DocumentAccessServiceV3
from deps_documents.domain.events import DocumentClassificationCompleted
from deps_documents.events_handler.handlers import (
    document_classification_completed_handler,
)


def test_document_classification_completed_handler(mocker):
    document_id = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex

    assign_document_type = mocker.patch.object(DocumentAccessServiceV3, "assign_document_type", return_value=None)

    dee = mocker.Mock(DomainEvent)
    dee.event = DocumentClassificationCompleted(
        document_id=document_id,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
    )

    document_classification_completed_handler(
        dee=dee,
    )

    assign_document_type.assert_called_with(document_id=document_id, tenant_id=tenant_id, document_type_id=document_type_id)
