import pytest

from deps_documents.domain.exceptions import (
    DocumentNotFoundError,
    LabelForDocumentNotFoundError,
    LabelNotFoundError,
)


@pytest.fixture()
def mocked_uow(uow):
    uow.document.remove_label.return_value = True

    return uow


@pytest.mark.usefixtures("mocked_uow")
class TestCaseDocumentRemoveLabelUseCase:
    def test_execute__valid_data__return_true(self, domain_services):
        result = domain_services.document().remove_label(document_entity_pk="1", label_pk="1")

        assert result

    def test_execute__not_exiting_label__return_error(self, domain_services, mocked_uow):
        mocked_uow.document.remove_label.side_effect = LabelNotFoundError

        with pytest.raises(LabelNotFoundError):
            domain_services.document().remove_label(document_entity_pk="1", label_pk="1")

    def test_execute__not_exiting_doc__return_error(self, domain_services, mocked_uow):
        mocked_uow.document.remove_label.side_effect = DocumentNotFoundError

        with pytest.raises(DocumentNotFoundError):
            domain_services.document().remove_label(document_entity_pk="1", label_pk="1")

    def test_execute__not_exiting_label_in_document__return_error(self, domain_services, mocked_uow):
        mocked_uow.document.remove_label.side_effect = LabelForDocumentNotFoundError

        with pytest.raises(LabelForDocumentNotFoundError):
            domain_services.document().remove_label(document_entity_pk="1", label_pk="1")
