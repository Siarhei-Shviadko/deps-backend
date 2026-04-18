from copy import deepcopy

import pytest

from deps_documents.domain.constants import DocumentPriorityEnum
from tests.factories import DocumentEntityFactory


@pytest.mark.priority
class TestUpdatePriorities:
    def test_update_priority__many_docs__batch_update_called(self, domain_services, uow, priority_managers):
        document_entity = DocumentEntityFactory()
        uow.document.get_list_by_filter.return_value = [deepcopy(document_entity)]
        priority_managers.time_in_processing().get_priority.return_value = DocumentPriorityEnum.HIGH
        document_entity.priority = DocumentPriorityEnum.HIGH

        domain_services.document().update_priorities()

        uow.document.batch_update.assert_called_with([document_entity])
