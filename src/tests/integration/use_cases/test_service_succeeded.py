from uuid import uuid4

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import Reviewer
from tests.factories import DocumentEntityFactory


def test_service_succeeded__reviewer_unassigned(use_cases, uow):
    document_repository = uow.document
    doc = document_repository.add(DocumentEntityFactory(reviewer=Reviewer(id=uuid4().hex)))
    assert doc.reviewer is not None

    use_case = use_cases.service_succeeded()

    use_case.execute(use_case.Request(document_id=doc.pk, unassign_reviewer=True))

    doc = document_repository.get(doc.pk)

    assert doc.state == DocumentStateEnum.COMPLETED
    assert doc.reviewer is None
