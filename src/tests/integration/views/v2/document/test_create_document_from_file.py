import json
from http import HTTPStatus
from io import BytesIO
from uuid import uuid4

from deps_documents.domain.entities import DocumentTypeEntity, ParsingFeature
from tests.factories import GroupEntityFactory


def test_create_document_from_file__with_all_parameters__document_created(
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
    metadata = {"test": "test", "key": "value"}

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
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()

    document_id = response_json.get("documentId")
    returned_document_name = response_json.get("documentName")

    assert document_id is not None
    assert returned_document_name == document_name

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


def test_create_document_from_file__with_minimal_parameters__document_created(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()

    document_id = response_json.get("documentId")
    returned_document_name = response_json.get("documentName")

    assert document_id is not None
    assert returned_document_name == document_name

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.document_type == document_type.id
    assert created_document.group_id is None


def test_create_document_from_file__with_optional_group__document_created(
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

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group.id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()

    document_id = response_json.get("documentId")
    returned_document_name = response_json.get("documentName")

    assert document_id is not None
    assert returned_document_name == document_name

    created_document = uow.document.get(document_id)

    assert created_document.title == document_name
    assert created_document.group_id == created_document.group.id == group.id


def test_create_document_from_file__with_metadata__metadata_parsed_correctly(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    metadata = {"key1": "value1", "key2": 123, "key3": True}

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "metadata": json.dumps(metadata),
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()
    document_id = response_json.get("documentId")

    created_document_metadata = uow.document.get_document_metadata(document_id)

    assert created_document_metadata.metadata == metadata


def test_create_document_from_file__with_invalid_metadata__error(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "metadata": "invalid json {",
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_document_from_file__document_type_not_found__error(
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

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_document_from_file__group_not_found__error(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    group_id = uuid4().hex
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "groupId": group_id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_document_from_file__with_parsing_features__features_set_correctly(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
        "parsingFeatures": json.dumps(list(parsing_features)),
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()
    document_id = response_json.get("documentId")

    created_document = uow.document.get(document_id)

    assert created_document.parsing_features == parsing_features


def test_create_document_from_file__response_contains_document_id_and_name(
    client, tenant_id, uow, user_fixture, fake_command_producer, set_test_user
):
    document_type = DocumentTypeEntity(id=uuid4().hex, tenant=tenant_id, name=uuid4().hex)
    uow.document_type.save(document_type)

    document_name = uuid4().hex
    document_type_id = document_type.id
    file_name = "document_file.jpg"
    file_content = b"a new document file content"

    data = {
        "documentName": document_name,
        "documentType": document_type_id,
    }

    files = {
        "file": (file_name, BytesIO(file_content), "application/jpg"),
    }

    response = client.post("/api-internal/document/documents/from-file", data=data, files=files)

    assert response.status_code == HTTPStatus.CREATED

    response_json = response.json()

    assert "documentId" in response_json
    assert "documentName" in response_json
    assert response_json["documentName"] == document_name
    assert response_json["documentId"] is not None
