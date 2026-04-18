from uuid import uuid4

import pytest

from deps_documents.domain.entities import ParsingFeature
from tests.factories import DocumentEntityFactory, GroupEntityFactory


@pytest.mark.application
def test_protected_create_document_from_file__success__returns_document_id_and_name(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    file_name = "test_document.pdf"
    file_content = b"test file content"
    assign_to_me = True

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
    )

    document_service_v3_mock.create_document.return_value = document

    result_document_id, result_document_name = application.document_access_v3().create_document_from_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=document.group_id,
        file_name=file_name,
        file_content=file_content,
        engine=document.engine,
        language=document.language,
        llm_type=document.llm_type,
        assign_to_me=assign_to_me,
    )

    assert result_document_id == document_id
    assert result_document_name == document_name
    document_access_manager_mock.check_is_accessible_create.assert_called_once()
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)
    document_service_v3_mock.create_document.assert_called_once()
    document_service_v3_mock.initiate_document_processing.assert_called_once()


@pytest.mark.application
def test_protected_create_document_from_file__with_all_parameters__calls_service_correctly(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    group = GroupEntityFactory()
    file_name = "test_document.pdf"
    file_content = b"test file content"
    engine = "tesseract"
    language = "en"
    llm_type = "gpt-4"
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = True
    needs_extraction = True
    needs_parsing = False
    assign_to_me = False
    metadata = {"key": "value"}

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
        group=group,
        engine=engine,
        language=language,
        llm_type=llm_type,
    )

    document_service_v3_mock.create_document.return_value = document

    result_document_id, result_document_name = application.document_access_v3().create_document_from_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group.id,
        file_name=file_name,
        file_content=file_content,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_parsing=needs_parsing,
    )

    assert result_document_id == document_id
    assert result_document_name == document_name

    document_service_v3_mock.create_document.assert_called_once()
    call_kwargs = document_service_v3_mock.create_document.call_args[1]
    assert call_kwargs["document_name"] == document_name
    assert call_kwargs["tenant_id"] == tenant_id
    assert call_kwargs["document_type_id"] == document_type_id
    assert call_kwargs["group_id"] == group.id
    assert call_kwargs["file_name"] == file_name
    assert call_kwargs["file_content"] == file_content
    assert call_kwargs["engine"] == engine
    assert call_kwargs["language"] == language
    assert call_kwargs["llm_type"] == llm_type
    assert call_kwargs["assign_to_me"] == assign_to_me
    assert call_kwargs["parsing_features"] == parsing_features
    assert call_kwargs["metadata"] == metadata
    assert call_kwargs["needs_unification"] == needs_unification
    assert call_kwargs["needs_extraction"] == needs_extraction
    assert call_kwargs["needs_parsing"] == needs_parsing

    document_service_v3_mock.initiate_document_processing.assert_called_once()
    processing_call_kwargs = document_service_v3_mock.initiate_document_processing.call_args[1]
    assert processing_call_kwargs["document"] == document
    assert processing_call_kwargs["tenant_id"] == tenant_id
    assert processing_call_kwargs["document_type_id"] == document_type_id
    assert processing_call_kwargs["group_id"] == group.id
    assert processing_call_kwargs["engine"] == engine
    assert processing_call_kwargs["language"] == language
    assert processing_call_kwargs["llm_type"] == llm_type
    assert processing_call_kwargs["parsing_features"] == parsing_features
    assert processing_call_kwargs["needs_unification"] == needs_unification
    assert processing_call_kwargs["needs_extraction"] == needs_extraction
    assert processing_call_kwargs["needs_parsing"] == needs_parsing


@pytest.mark.application
def test_protected_create_document_from_file__with_minimal_parameters__calls_service_correctly(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    file_name = "test_document.pdf"
    file_content = b"test file content"

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
    )

    document_service_v3_mock.create_document.return_value = document

    result_document_id, result_document_name = application.document_access_v3().create_document_from_file(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=None,
        file_name=file_name,
        file_content=file_content,
        engine=None,
        language=None,
        llm_type=None,
        assign_to_me=False,
    )

    assert result_document_id == document_id
    assert result_document_name == document_name

    document_service_v3_mock.create_document.assert_called_once()
    call_kwargs = document_service_v3_mock.create_document.call_args[1]
    assert call_kwargs["document_name"] == document_name
    assert call_kwargs["tenant_id"] == tenant_id
    assert call_kwargs["document_type_id"] == document_type_id
    assert call_kwargs["group_id"] is None
    assert call_kwargs["file_name"] == file_name
    assert call_kwargs["file_content"] == file_content
    assert call_kwargs["engine"] is None
    assert call_kwargs["language"] is None
    assert call_kwargs["llm_type"] is None
    assert call_kwargs["assign_to_me"] is False
    assert call_kwargs["parsing_features"] is None
    assert call_kwargs["metadata"] is None
    assert call_kwargs["needs_unification"] is False
    assert call_kwargs["needs_extraction"] is False
    assert call_kwargs["needs_parsing"] is False

    document_service_v3_mock.initiate_document_processing.assert_called_once()


@pytest.mark.application
def test_protected_create_document__with_all_parameters__calls_service_correctly(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    group = GroupEntityFactory()
    file_name = "test_document.pdf"
    file_content = b"test file content"
    engine = "tesseract"
    language = "en"
    llm_type = "gpt-4"
    parsing_features = {ParsingFeature.TEXT, ParsingFeature.IMAGES}
    needs_unification = True
    needs_extraction = True
    needs_parsing = False
    assign_to_me = False
    metadata = {"key": "value"}

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
        group=group,
        engine=engine,
        language=language,
        llm_type=llm_type,
    )

    document_service_v3_mock.create_document.return_value = document

    result_document_id = application.document_access_v3().create_document(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=group.id,
        file_name=file_name,
        file_content=file_content,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        metadata=metadata,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_parsing=needs_parsing,
    )

    assert result_document_id == document_id

    document_service_v3_mock.create_document.assert_called_once()
    call_kwargs = document_service_v3_mock.create_document.call_args[1]
    assert call_kwargs["document_name"] == document_name
    assert call_kwargs["tenant_id"] == tenant_id
    assert call_kwargs["document_type_id"] == document_type_id
    assert call_kwargs["group_id"] == group.id
    assert call_kwargs["file_name"] == file_name
    assert call_kwargs["file_content"] == file_content
    assert call_kwargs["engine"] == engine
    assert call_kwargs["language"] == language
    assert call_kwargs["llm_type"] == llm_type
    assert call_kwargs["assign_to_me"] == assign_to_me
    assert call_kwargs["parsing_features"] == parsing_features
    assert call_kwargs["metadata"] == metadata
    assert call_kwargs["needs_unification"] == needs_unification
    assert call_kwargs["needs_extraction"] == needs_extraction
    assert call_kwargs["needs_parsing"] == needs_parsing

    document_service_v3_mock.initiate_document_processing.assert_called_once()
    processing_call_kwargs = document_service_v3_mock.initiate_document_processing.call_args[1]
    assert processing_call_kwargs["document"] == document
    assert processing_call_kwargs["tenant_id"] == tenant_id
    assert processing_call_kwargs["document_type_id"] == document_type_id
    assert processing_call_kwargs["group_id"] == group.id
    assert processing_call_kwargs["engine"] == engine
    assert processing_call_kwargs["language"] == language
    assert processing_call_kwargs["llm_type"] == llm_type
    assert processing_call_kwargs["parsing_features"] == parsing_features
    assert processing_call_kwargs["needs_unification"] == needs_unification
    assert processing_call_kwargs["needs_extraction"] == needs_extraction
    assert processing_call_kwargs["needs_parsing"] == needs_parsing

    document_access_manager_mock.check_is_accessible_create.assert_called_once()
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)


@pytest.mark.application
def test_protected_create_document__with_minimal_parameters__calls_service_correctly(
    application,
    document_service_v3_mock,
    document_access_manager_mock,
):
    document_id = uuid4().hex
    document_name = uuid4().hex
    tenant_id = uuid4().hex
    document_type_id = uuid4().hex
    file_name = "test_document.pdf"
    file_content = b"test file content"

    document = DocumentEntityFactory(
        pk=document_id,
        title=document_name,
        document_type=document_type_id,
    )

    document_service_v3_mock.create_document.return_value = document

    result_document_id = application.document_access_v3().create_document(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        group_id=None,
        file_name=file_name,
        file_content=file_content,
        engine=None,
        language=None,
        llm_type=None,
        assign_to_me=False,
    )

    assert result_document_id == document_id

    document_service_v3_mock.create_document.assert_called_once()
    call_kwargs = document_service_v3_mock.create_document.call_args[1]
    assert call_kwargs["document_name"] == document_name
    assert call_kwargs["tenant_id"] == tenant_id
    assert call_kwargs["document_type_id"] == document_type_id
    assert call_kwargs["group_id"] is None
    assert call_kwargs["file_name"] == file_name
    assert call_kwargs["file_content"] == file_content
    assert call_kwargs["engine"] is None
    assert call_kwargs["language"] is None
    assert call_kwargs["llm_type"] is None
    assert call_kwargs["assign_to_me"] is False
    assert call_kwargs["parsing_features"] is None
    assert call_kwargs["metadata"] is None
    assert call_kwargs["needs_unification"] is False
    assert call_kwargs["needs_extraction"] is False
    assert call_kwargs["needs_parsing"] is None
    assert call_kwargs["needs_validation"] is None
    assert call_kwargs["needs_output_exporting"] is None
    assert call_kwargs["needs_review"] is None

    document_service_v3_mock.initiate_document_processing.assert_called_once()

    document_access_manager_mock.check_is_accessible_create.assert_called_once()
    document_access_manager_mock.add_permissions_after_creating.assert_called_with(document_id)
