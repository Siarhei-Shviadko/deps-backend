import pytest

from deps_documents.domain.constants import (
    PROCESSING_STATES,
    DocumentStateEnum,
    PipelineStepsEnum,
)
from deps_documents.domain.exceptions import DocumentStateError
from tests.factories import BlobFileFactory, DocumentEntityFactory


class TestRunPipelineFromStepUseCase:
    def test_execute__valid_data__correct_response(self, domain_services, uow):
        document_ids = [str(i) for i in range(3)]
        documents = [self._get_document(document_id) for document_id in document_ids]
        uow.document.find_by_pks.return_value = list(documents)

        result = domain_services.document().run_pipeline_from_step(
            document_ids, step=PipelineStepsEnum.EXTRACTION, engine="TESSERACT", language="eng"
        )

        assert sorted(document_ids) == sorted([document.pk for document in result])

    def test_execute__invalid_document_id_is_skipped(self, domain_services, uow):
        document_ids = [str(i) for i in range(3)]
        documents = [self._get_document(document_id) for document_id in document_ids]
        uow.document.find_by_pks.return_value = list(documents)

        request_document_ids = document_ids.copy()
        request_document_ids.append("bad_id")
        result = domain_services.document().run_pipeline_from_step(
            request_document_ids, step=PipelineStepsEnum.EXTRACTION, language="eng"
        )

        assert sorted(document_ids) == sorted([document.pk for document in result])

    def test_execute__run_from_preprocess_step(self, domain_services, uow):
        document = self._get_document()
        uow.document.find_by_pks.return_value = [document]

        domain_services.document().run_pipeline_from_step([document.pk], step=PipelineStepsEnum.PREPROCESS, language="eng")

        updated_document = self._get_document_update_call_args(uow)

        assert not updated_document.preview_documents
        assert not updated_document.processing_documents
        assert not updated_document.document_type

    def test_execute__run_from_identification_step(self, domain_services, uow):
        document = self._get_document()
        uow.document.find_by_pks.return_value = [document]

        domain_services.document().run_pipeline_from_step([document.pk], step=PipelineStepsEnum.IDENTIFICATION, language="eng")

        updated_document = self._get_document_update_call_args(uow)

        assert updated_document.preview_documents
        assert updated_document.processing_documents
        assert not updated_document.document_type

    def test_execute__run_from_extraction_step(self, domain_services, uow):
        document = self._get_document()
        uow.document.find_by_pks.return_value = [document]

        domain_services.document().run_pipeline_from_step([document.pk], step=PipelineStepsEnum.EXTRACTION, language="eng")

        updated_document = self._get_document_update_call_args(uow)

        assert updated_document.preview_documents
        assert updated_document.processing_documents
        assert updated_document.document_type

    def test_execute__document_wrong_state__raises_error(self, domain_services, uow):
        document_id_to_state = {str(id): state for id, state in enumerate(PROCESSING_STATES)}
        documents = [DocumentEntityFactory(pk=id, state=state) for id, state in document_id_to_state.items()]

        uow.document.find_by_pks.return_value = list(documents)

        with pytest.raises(DocumentStateError):
            domain_services.document().run_pipeline_from_step(
                list(document_id_to_state.keys()), step=PipelineStepsEnum.EXTRACTION, language="eng"
            )

    @staticmethod
    def _get_document(document_id=1):
        return DocumentEntityFactory(
            pk=str(document_id),
            preview_documents=[BlobFileFactory() for i in range(2)],
            processing_documents=[BlobFileFactory() for i in range(2)],
            document_type="BelarusPassport",
            state=DocumentStateEnum.COMPLETED,
        )

    @staticmethod
    def _get_document_update_call_args(uow):
        document_update_call = uow.document.update
        assert document_update_call.called
        return document_update_call.call_args[0][0]
