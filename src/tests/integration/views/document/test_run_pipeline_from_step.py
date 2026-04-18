import pytest

from deps_documents.domain.constants import (
    PROCESSING_STATES,
    DocumentStateEnum,
    PipelineStepsEnum,
)
from deps_documents.domain.exceptions import PrimaryKeyError
from tests.factories import BlobFileFactory, DocumentEntityFactory


class TestRunPipelineFromStepView:
    def test_post__valid_params__200(self, client, uow):
        document_ids = [str(i) for i in range(1, 4)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.COMPLETED) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": document_ids, "step": PipelineStepsEnum.IDENTIFICATION.value, "engineName": "TESSERACT"},
        )
        response_json = response.json()

        assert response.status_code == 200
        assert sorted(d["_id"] for d in response_json) == sorted(document_ids)

    def test_post__document_not_exists__return_404(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": ["1"], "step": PipelineStepsEnum.IDENTIFICATION.value, "engineName": "TESSERACT"},
        )

        assert response.status_code == 404

    def test_post__missing_engine_name__200(self, client, uow):
        document_ids = [str(i) for i in range(1, 4)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.COMPLETED) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": document_ids, "step": PipelineStepsEnum.IDENTIFICATION.value},
        )
        assert response.status_code == 200

    def test_post__missing_step__422(self, client, uow):
        document = DocumentEntityFactory(pk="1")

        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step", json={"documentIds": [document.pk], "engineName": "TESSERACT"}
        )

        assert response.status_code == 422

    def test_post__missing_document_id__422(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"step": PipelineStepsEnum.EXTRACTION.value, "engineName": "TESSERACT"},
        )
        assert response.status_code == 422

    def test_post__invalid_document_ids__raise_exception(self, client, uow):
        with pytest.raises(PrimaryKeyError):
            uow.document.find_by_pks(document_pks=["hey"])

    def test_post__preprocess_step_200(self, client, uow):
        document = self._create_document(uow)
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": [document.pk], "step": PipelineStepsEnum.PREPROCESS.value},
        )

        assert response.status_code == 200

        updated_document = uow.document.get(document.pk)
        assert not updated_document.preview_documents
        assert not updated_document.processing_documents
        assert not updated_document.document_type

    def test_post__identification_step_200(self, client, uow):
        document = self._create_document(uow)
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": [document.pk], "step": PipelineStepsEnum.IDENTIFICATION.value},
        )

        assert response.status_code == 200

        updated_document = uow.document.get(document.pk)
        assert updated_document.preview_documents
        assert updated_document.processing_documents
        assert not updated_document.document_type

    def test_post__extraction_step__200(self, client, uow):
        document = self._create_document(uow)
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": [document.pk], "step": PipelineStepsEnum.EXTRACTION.value},
        )

        assert response.status_code == 200

        updated_document = uow.document.get(document.pk)
        assert updated_document.preview_documents
        assert updated_document.processing_documents
        assert updated_document.document_type

    def test_post__documents_in_processing__return_400(self, client, uow):
        document_id_to_state = {str(pk): state for pk, state in enumerate(PROCESSING_STATES, 1)}
        documents = [
            DocumentEntityFactory(pk=pk, state=state, document_type="BelarusPassport")
            for pk, state in document_id_to_state.items()
        ]

        for document in documents:
            uow.document.add(document)

        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": list(document_id_to_state.keys()), "step": PipelineStepsEnum.EXTRACTION.value},
        )

        assert response.status_code == 400

    @staticmethod
    def _create_document(uow):
        document = uow.document.add(
            DocumentEntityFactory(
                pk="1",
                preview_documents=[BlobFileFactory()],
                processing_documents=[BlobFileFactory()],
                title="Some document",
                document_type="BelarusPassport",
                state=DocumentStateEnum.COMPLETED,
            )
        )
        return document
