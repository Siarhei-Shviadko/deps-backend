import json
from http import HTTPStatus
from io import BytesIO
from uuid import uuid4

from deps_documents.domain.entities import ParsingFeature
from tests.factories import DocumentEntityFactory


def test_create_document(client, document_service_v3_mock, tenant_id):
    document_id = uuid4().hex
    document_name = uuid4().hex
    document_type_id = uuid4().hex
    file_content = b"qwerty"
    parsing_features = ["text", "kvps", "tables"]
    assign_to_me = True
    metadata = {"test": "test"}
    needs_review = "always_review"
    needs_validation = True
    needs_output_exporting = True
    needs_parsing = True

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
        parsing_features=parsing_features,
        needs_review=needs_review,
        needs_validation=needs_validation,
        needs_output_exporting=needs_output_exporting,
        needs_parsing=needs_parsing,
    )

    file_name = document.blob_names[0]

    document_service_v3_mock.create_document.return_value = document

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": document.group_id,
        "engine": document.engine,
        "language": document.language,
        "llmType": document.llm_type,
        "parsingFeatures": json.dumps(parsing_features),
        "needsUnifier": document.needs_unification,
        "needsExtraction": document.needs_extraction,
        "needsParsing": document.needs_parsing,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
        "needsReview": document.needs_review,
        "needsValidation": document.needs_validation,
        "needsOutputExporting": document.needs_output_exporting,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_json.get("id") == document_id

    document_service_v3_mock.create_document.assert_called_with(
        tenant_id=tenant_id,
        document_name=document_name,
        file_content=file_content,
        file_name=file_name,
        group_id=document.group_id,
        document_type_id=document_type_id,
        engine=document.engine,
        language=document.language,
        assign_to_me=assign_to_me,
        parsing_features={ParsingFeature(feature) for feature in parsing_features},
        metadata=metadata,
        needs_unification=document.needs_unification,
        needs_extraction=document.needs_extraction,
        needs_parsing=document.needs_parsing,
        parent_id=None,
        llm_type=document.llm_type,
        label_ids=None,
        needs_review=document.needs_review,
        needs_validation=document.needs_validation,
        needs_output_exporting=document.needs_output_exporting,
    )


def test_create_document_without_optional_processing_params(client, document_service_v3_mock, tenant_id):
    document_id = uuid4().hex
    document_name = uuid4().hex
    document_type_id = uuid4().hex
    file_content = b"qwerty"
    parsing_features = ["text", "kvps", "tables"]
    assign_to_me = True
    metadata = {"test": "test"}
    needs_review = None
    needs_validation = None
    needs_output_exporting = None
    needs_parsing = None

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
        parsing_features=parsing_features,
        needs_review=needs_review,
        needs_validation=needs_validation,
        needs_output_exporting=needs_output_exporting,
        needs_parsing=needs_parsing,
    )

    file_name = document.blob_names[0]

    document_service_v3_mock.create_document.return_value = document

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": document.group_id,
        "engine": document.engine,
        "language": document.language,
        "llmType": document.llm_type,
        "parsingFeatures": json.dumps(parsing_features),
        "needsUnifier": document.needs_unification,
        "needsExtraction": document.needs_extraction,
        "needsParsing": document.needs_parsing,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_json.get("id") == document_id

    document_service_v3_mock.create_document.assert_called_with(
        tenant_id=tenant_id,
        document_name=document_name,
        file_content=file_content,
        file_name=file_name,
        group_id=document.group_id,
        document_type_id=document_type_id,
        engine=document.engine,
        language=document.language,
        assign_to_me=assign_to_me,
        parsing_features={ParsingFeature(feature) for feature in parsing_features},
        metadata=metadata,
        needs_unification=document.needs_unification,
        needs_extraction=document.needs_extraction,
        needs_parsing=document.needs_parsing,
        parent_id=None,
        llm_type=document.llm_type,
        label_ids=None,
        needs_review=None,
        needs_validation=None,
        needs_output_exporting=None,
    )
