from datetime import datetime, timedelta, timezone

import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import CommunicationEntityFactory, DocumentEntityFactory


@pytest.mark.priority
class TestUpdatePriority:
    def test_update_priority__priority_updated(self, uow, domain_services, app):
        high_boundary = app.container.config.priority.high_boundary()
        create_date = datetime.now(tz=timezone.utc) - timedelta(seconds=high_boundary)
        document_entity = uow.document.add(DocumentEntityFactory(date=create_date))

        domain_services.document().update_priorities()

        assert document_entity == uow.document.get(document_entity.pk)
