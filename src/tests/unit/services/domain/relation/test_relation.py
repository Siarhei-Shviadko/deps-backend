import pytest

from deps_documents.domain.exceptions import DocumentAssigningError
from tests.factories import RelationEntityFactory


def test_create_relation__docs_does__not_exists__exist_error(uow, relation_service):
    relation = RelationEntityFactory()
    uow.relation.assign_document.side_effect = DocumentAssigningError(relation.assigned_documents)

    with pytest.raises(DocumentAssigningError):
        relation_service.create_relation(relation)
