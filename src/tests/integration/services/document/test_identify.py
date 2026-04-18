import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentNotAcceptableStateError
from tests.factories import DocumentEntityFactory


class TestDocumentServiceIdentify:
    def test_identify_not_valid_document_state_raise_error(self, uow, domain_services):
        document_entity = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.NEW))
        with pytest.raises(DocumentNotAcceptableStateError) as exc_error:
            domain_services.document().identify([document_entity.pk])

        assert exc_error.value.args[0] == f"Document ({document_entity.pk}) has 'Unacceptable' identification document state."

    def test_identify_valid_data_return_correct_answer(self, uow, domain_services):
        document_entity = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.FAILED))
        result = domain_services.document().identify([document_entity.pk])

        assert result[0].error is None
        assert result[0].state == DocumentStateEnum.IDENTIFICATION
