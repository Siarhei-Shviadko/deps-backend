from itertools import product

import pytest

from deps_documents.domain.entities import DocumentEntity, DocumentEntityPk
from deps_documents.domain.exceptions import DocumentLastStepRetrievingError
from deps_documents.domain.specifications import (
    CanBeRetried,
    CanBeRetriedExtraction,
    CanBeRetriedIdentification,
    CanBeRetriedPreprocessing,
)
from tests.factories import DocumentEntityFactory


class TestDocumentRetryLastStepUseCase:
    def test_execute__can_be_retried__response_value_document(self, domain_services, mocker, uow, services):
        mock_repository = mocker.patch.multiple(
            uow.document, clear_error=mocker.DEFAULT, update_state=mocker.DEFAULT, get=mocker.DEFAULT
        )
        mock_repository["get"].return_value = DocumentEntityFactory()

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = True

        mocker.patch.object(services.pipeline_manager(), "run_from_step")

        mock_can_be_extracted = mocker.patch.object(CanBeRetriedExtraction, "is_satisfied_by")
        mock_can_be_extracted.return_value = True

        result = domain_services.document().retry_last_step(DocumentEntityPk("1"))

        assert isinstance(result, DocumentEntity)

    def test_execute__can_not_be_retried__response_value_error(self, domain_services, mocker, uow):
        mock_repository = mocker.patch.multiple(uow.document, get=mocker.DEFAULT)
        mock_repository["get"].return_value = DocumentEntityFactory()

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = False

        with pytest.raises(DocumentLastStepRetrievingError):
            domain_services.document().retry_last_step(DocumentEntityPk("1"))

    @pytest.mark.parametrize("test_specification", product((True, False), repeat=3))
    def test_execute__many_specification_responses__return_document_or_none(
        self, domain_services, mocker, test_specification, uow, services
    ):
        mock_repository = mocker.patch.multiple(
            uow.document, clear_error=mocker.DEFAULT, update_state=mocker.DEFAULT, get=mocker.DEFAULT
        )
        mock_repository["get"].return_value = DocumentEntityFactory()

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = True

        mocker.patch.object(services.pipeline_manager(), "run_from_step")

        mock_can_be_extracted = mocker.patch.object(CanBeRetriedExtraction, "is_satisfied_by")
        mock_can_be_identified = mocker.patch.object(CanBeRetriedIdentification, "is_satisfied_by")
        mock_can_be_preprocessed = mocker.patch.object(CanBeRetriedPreprocessing, "is_satisfied_by")

        (
            mock_can_be_extracted.return_value,
            mock_can_be_identified.return_value,
            mock_can_be_preprocessed.return_value,
        ) = test_specification

        if any(test_specification):
            result = domain_services.document().retry_last_step(DocumentEntityPk("1"))
            assert bool(result) == any(test_specification)
        else:
            with pytest.raises(DocumentLastStepRetrievingError):
                domain_services.document().retry_last_step(DocumentEntityPk("1"))

    def test_execute__can_be_extracted__called_extraction_service_and_repository_methods(
        self, domain_services, mocker, uow, services
    ):
        mock_repository = mocker.patch.multiple(
            uow.document,
            clear_error=mocker.DEFAULT,
            update_state=mocker.DEFAULT,
            get=mocker.DEFAULT,
            update=mocker.DEFAULT,
        )
        mock_repository["get"].return_value = DocumentEntityFactory(pk="1")

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = True

        mock_pipeline_manager_run_from_step = mocker.patch.object(services.pipeline_manager(), "run_from_step")

        mock_can_be_extracted = mocker.patch.object(CanBeRetriedExtraction, "is_satisfied_by")
        mock_can_be_extracted.return_value = True

        domain_services.document().retry_last_step(DocumentEntityPk("1"))

        mock_pipeline_manager_run_from_step.assert_called()
        mock_repository["update"].assert_called_once()

    def test_execute__can_be_identified__called_identification_service_and_repository_methods(
        self, domain_services, mocker, uow, services
    ):
        mock_repository = mocker.patch.multiple(uow.document, update=mocker.DEFAULT, get=mocker.DEFAULT)
        mock_repository["get"].return_value = DocumentEntityFactory()

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = True

        mock_pipeline_manager_run_from_step = mocker.patch.object(services.pipeline_manager(), "run_from_step")

        mock_can_be_extracted = mocker.patch.object(CanBeRetriedExtraction, "is_satisfied_by")
        mock_can_be_extracted.return_value = False
        mock_can_be_identified = mocker.patch.object(CanBeRetriedIdentification, "is_satisfied_by")
        mock_can_be_identified.return_value = True

        domain_services.document().retry_last_step(DocumentEntityPk("1"))

        mock_pipeline_manager_run_from_step.assert_called()
        mock_repository["update"].assert_called_once()

    def test_execute__can_be_preprocessed__called_preprocess_service_and_repository_methods(
        self, domain_services, mocker, uow, services
    ):
        mock_repository = mocker.patch.multiple(uow.document, update=mocker.DEFAULT, get=mocker.DEFAULT)
        mock_repository["get"].return_value = DocumentEntityFactory()

        mock_can_be_retried = mocker.patch.object(CanBeRetried, "is_satisfied_by")
        mock_can_be_retried.return_value = True

        mock_pipeline_manager_run_from_step = mocker.patch.object(services.pipeline_manager(), "run_from_step")

        mock_can_be_extracted = mocker.patch.object(CanBeRetriedExtraction, "is_satisfied_by")
        mock_can_be_extracted.return_value = False
        mock_can_be_identified = mocker.patch.object(CanBeRetriedIdentification, "is_satisfied_by")
        mock_can_be_identified.return_value = False
        mock_can_be_preprocessed = mocker.patch.object(CanBeRetriedPreprocessing, "is_satisfied_by")
        mock_can_be_preprocessed.return_value = True

        domain_services.document().retry_last_step(DocumentEntityPk("1"))

        mock_pipeline_manager_run_from_step.assert_called()
        mock_repository["update"].assert_called_once()
