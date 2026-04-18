import pytest

from deps_documents.domain.dtos import BatchResponseObject
from deps_documents.domain.exceptions import LabelNotFoundError
from tests.factories import DocumentEntityFactory


@pytest.fixture()
def mocked_uow(uow):
    document_ids = [str(i) for i in range(1, 3)]
    uow.document.find_by_pks.return_value = [DocumentEntityFactory(pk=document_id) for document_id in document_ids]

    yield uow


@pytest.mark.usefixtures("mocked_uow")
class TestCaseDocumentAddLabelUseCase:
    def test_execute__many_data(self, domain_services):
        result = domain_services.document().add_label(document_entity_pks=["1", "2"], label_pk="1")

        assert {document.pk for document in result} == {"1", "2"}

    def test_execute__not_exiting_label__return_error(self, domain_services, mocked_uow):
        mocked_uow.document.add_label.side_effect = LabelNotFoundError

        with pytest.raises(LabelNotFoundError):
            domain_services.document().add_label(document_entity_pks=["1", "2", "3", "a"], label_pk="1")
