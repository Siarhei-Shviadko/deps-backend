import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import DocumentNotAcceptableStateError
from tests.factories import DocumentEntityFactory


class TestDocumentIdentifyDocumentUseCase:
    def test_execute__valid_data__return_success(self, domain_services, services, uow):
        run_step_mock = services.pipeline_manager().run_step
        document_1 = DocumentEntityFactory(pk=1, state=DocumentStateEnum.COMPLETED)
        document_2 = DocumentEntityFactory(pk=2, state=DocumentStateEnum.COMPLETED)

        select_for_update_mock = uow.document.select_for_update
        select_for_update_mock.return_value = [
            document_1,
            document_2,
        ]
        batch_update_mock = uow.document.batch_update

        batch_update_mock.return_value = [
            document_1,
            document_2,
        ]

        result = domain_services.document().identify([DocumentEntityPk("1"), DocumentEntityPk("2")])
        excpected_result = [document_1, document_2]

        assert run_step_mock.call_count == 2
        assert result == excpected_result

    @pytest.mark.skip("Tests same case as function above")
    def test_process_request__existing_docs(self, domain_services, uow):
        mock_set_identification_state = domain_services.document().identify
        mock_set_identification_state.return_value = [DocumentEntityPk("1"), DocumentEntityPk("2")]

        mock_find_by_pks = uow.document.find_by_pks
        mock_find_by_pks.return_value = []
        expected_response = [DocumentEntityPk("1"), DocumentEntityPk("2")]

        result = domain_services.document().identify([DocumentEntityPk("1"), DocumentEntityPk("2")])

        mock_set_identification_state.assert_called_once()
        assert result == expected_response

    def test_identify__document_wrong_state__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.PREPROCESSING)

        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentNotAcceptableStateError):
            domain_services.document().identify(document.pk)
