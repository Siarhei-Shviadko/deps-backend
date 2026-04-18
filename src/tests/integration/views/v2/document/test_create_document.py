import json
from http import HTTPStatus
from io import BytesIO
from uuid import uuid4

from deps_documents.domain.entities import (
    DocumentTypeEntity,
    LabelEntity,
    ParsingFeature,
)
from deps_documents.domain.model import ClassifyDocument, ProcessDocument
from tests.factories import GroupEntityFactory


def test_create_document__with_document_type__with_group(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    group = GroupEntityFactory()
    uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = False
    needs_extraction = False
    assign_to_me = True
    metadata = {"test": "test"}
    needs_review = "always_review"
    needs_parsing = False
    needs_validation = None
    needs_output_exporting = None

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group.id,
        "engine": engine,
        "language": language,
        "llmType": llm_type,
        "parsingFeatures": json.dumps(list(parsing_features)),
        "needsUnifier": needs_unification,
        "needsExtraction": needs_extraction,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
        "needsReview": needs_review,
        "needsParsing": needs_parsing,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    document_id = response_json.get("id")

    assert document_id is not None

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.document_type == document_type.id
    assert created_document.engine == engine
    assert created_document.language == language
    assert created_document.llm_type == llm_type
    assert created_document.group_id == created_document.group.id == group.id
    assert created_document.group.name == group.name
    assert len(created_document.files) == 1
    assert created_document.reviewer.id == user_fixture["subject"]
    assert created_document.parsing_features == parsing_features
    assert created_document.needs_extraction == needs_extraction
    assert created_document.needs_unification == needs_unification
    assert created_document.needs_review == needs_review
    assert created_document.needs_validation is needs_validation
    assert created_document.needs_output_exporting is needs_output_exporting
    assert created_document.needs_parsing is False

    assert fake_command_producer.last_sended
    assert fake_command_producer.last_sended.command == ProcessDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        files=created_document.blob_names,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=sorted(parsing_features),
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_review=needs_review,
        needs_validation=needs_validation,
        needs_output_exporting=needs_output_exporting,
        needs_parsing=needs_parsing,
    )


def test_create_document__without_document_type__without_group(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_name = uuid4().hex
    document_type_id = None
    group_id = None
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = False
    needs_extraction = False
    assign_to_me = True
    metadata = {"test": "test"}
    needs_parsing = False
    needs_validation = None
    needs_output_exporting = None
    needs_review = "always_review"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group_id,
        "engine": engine,
        "language": language,
        "llmType": llm_type,
        "parsingFeatures": json.dumps(list(parsing_features)),
        "needsUnifier": needs_unification,
        "needsExtraction": needs_extraction,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
        "needsParsing": needs_parsing,
        "needsReview": needs_review,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    document_id = response_json.get("id")

    assert document_id is not None

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.document_type == document_type_id
    assert created_document.engine == engine
    assert created_document.language == language
    assert created_document.llm_type == llm_type
    assert created_document.group_id == group_id
    assert len(created_document.files) == 1
    assert created_document.reviewer.id == user_fixture["subject"]
    assert created_document.parsing_features == parsing_features
    assert created_document.needs_extraction == needs_extraction
    assert created_document.needs_unification == needs_unification
    assert created_document.needs_validation is needs_validation
    assert created_document.needs_output_exporting is needs_output_exporting
    assert created_document.needs_parsing is needs_parsing
    assert created_document.needs_review == needs_review

    assert fake_command_producer.last_sended
    assert fake_command_producer.last_sended.command == ProcessDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        files=created_document.blob_names,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=sorted(parsing_features),
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_validation=needs_validation,
        needs_output_exporting=needs_output_exporting,
        needs_parsing=needs_parsing,
        needs_review=needs_review,
    )


def test_create_document__without_document_type__with_group(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    group = GroupEntityFactory()
    uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)

    document_name = uuid4().hex
    document_type_id = None
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = False
    needs_extraction = False
    assign_to_me = True
    metadata = {"test": "test"}
    needs_parsing = False
    needs_validation = None
    needs_output_exporting = None
    needs_review = "always_review"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group.id,
        "engine": engine,
        "language": language,
        "llmType": llm_type,
        "parsingFeatures": json.dumps(list(parsing_features)),
        "needsUnifier": needs_unification,
        "needsExtraction": needs_extraction,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
        "needsParsing": needs_parsing,
        "needsReview": needs_review,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    document_id = response_json.get("id")

    assert document_id is not None

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.document_type == document_type_id
    assert created_document.engine == engine
    assert created_document.language == language
    assert created_document.llm_type == llm_type
    assert created_document.group_id == created_document.group.id == group.id
    assert created_document.group.name == group.name
    assert len(created_document.files) == 1
    assert created_document.reviewer.id == user_fixture["subject"]
    assert created_document.parsing_features == parsing_features
    assert created_document.needs_extraction == needs_extraction
    assert created_document.needs_unification == needs_unification
    assert created_document.needs_validation is needs_validation
    assert created_document.needs_output_exporting is needs_output_exporting
    assert created_document.needs_parsing is needs_parsing
    assert created_document.needs_review == needs_review

    assert fake_command_producer.last_sended
    assert fake_command_producer.last_sended.command == ClassifyDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        group_id=group.id,
        files=created_document.blob_names,
        engine=engine,
        language=language,
        parsing_features=list(parsing_features),
    )


def test_create_document__document_type_does_not_exist__error(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_name = uuid4().hex
    document_type_id = uuid4().hex
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_document__group_does_not_exist__error(client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user):
    document_name = uuid4().hex
    group_id = uuid4().hex
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "groupId": group_id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_document__group_is_deleted__error(client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user):
    group = GroupEntityFactory()
    uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)
    uow.group.mark_deleted(group_id=group.id, tenant_id=tenant_id)

    document_name = uuid4().hex
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "groupId": group.id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_document__without_document_type__without_group__with_labels(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_name = uuid4().hex
    document_type_id = None
    group_id = None
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = False
    needs_extraction = False
    assign_to_me = True
    metadata = {"test": "test"}
    label = uow.label.add(LabelEntity("Test label"))

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group_id,
        "engine": engine,
        "language": language,
        "llmType": llm_type,
        "parsingFeatures": json.dumps(list(parsing_features)),
        "needsUnifier": needs_unification,
        "needsExtraction": needs_extraction,
        "assignedToMe": assign_to_me,
        "metadata": json.dumps(metadata),
        "labelIds": json.dumps([label.pk]),
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api/document/v2/documents", data=data, files=files)

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    document_id = response_json.get("id")

    assert document_id is not None

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.document_type == document_type_id
    assert created_document.engine == engine
    assert created_document.language == language
    assert created_document.llm_type == llm_type
    assert created_document.group_id == group_id
    assert len(created_document.files) == 1
    assert created_document.reviewer.id == user_fixture["subject"]
    assert created_document.parsing_features == parsing_features
    assert created_document.needs_extraction == needs_extraction
    assert created_document.needs_unification == needs_unification
    assert created_document.labels[0].name == "Test label"

    assert fake_command_producer.last_sended
    assert fake_command_producer.last_sended.command == ProcessDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        files=created_document.blob_names,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=sorted(parsing_features),
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
    )
