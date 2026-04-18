import uuid

import pytest

from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.dtos import (
    DocumentFilesDataObject,
    DocumentListDataObject,
    DocumentListFilterObject,
)
from deps_documents.domain.entities import CommentEntity, DocumentEntity
from tests.factories.document_entity import (
    CommentEntityFactory,
    DocumentEntityFactory,
    DocumentFilesDataFactory,
    DocumentListDataFactory,
)


@pytest.mark.usefixtures("enable_authorization_for_container", "set_test_user")
class TestDocumentServiceAccessor:
    document_pk = "1"
    document_entity = DocumentEntityFactory(pk=document_pk)

    def test_add_comment__user_has_access__comment_added(
        self, document_service_mock, document_access_manager_mock, label_access_manager_mock, domain_services_accessor
    ):
        comment_entity = CommentEntityFactory()
        document_service_mock.add_comment.return_value = comment_entity

        result = domain_services_accessor.document().add_comment(
            comment_entity=comment_entity, document_entity_pk=self.document_pk
        )

        assert isinstance(result, CommentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_add_file__user_has_access__document_added__token_is_set(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.add_file.return_value = self.document_pk
        result = domain_services_accessor.document().add_file(
            self.document_pk,
            file_content=b"",
            file_name="file_name",
        )

        assert result == self.document_pk
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_add_label__user_has_access__label_added(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.add_label.return_value = [self.document_entity]
        result = domain_services_accessor.document().add_label(document_entity_pks=[self.document_pk], label_pk="1")

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_assign_type__user_has_access__type_assigned(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.assign_type.return_value = [self.document_entity]
        result = domain_services_accessor.document().assign_type([self.document_pk], "TestDocType")

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_batch_delete__user_has_access__deleted__token_is_set(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.batch_delete.return_value = [self.document_entity]
        result = domain_services_accessor.document().batch_delete([self.document_pk])

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_complete_review__user_has_access__review_completed(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.complete_review.return_value = self.document_entity
        result = domain_services_accessor.document().complete_review(self.document_pk)

        assert isinstance(result, DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_create__user_has_access__created(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.create.return_value = self.document_pk
        result = domain_services_accessor.document().create(self.document_entity)

        assert result == self.document_pk
        document_access_manager_mock.check_is_accessible_create.assert_called_once()
        document_access_manager_mock.add_permissions_after_creating.assert_called_with(self.document_pk)

    def test_delete__user_has_access__deleted__token_is_set(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.delete.return_value = True
        result = domain_services_accessor.document().delete(self.document_pk)

        assert result is True
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_document_file__user_has_access__document_created__token_is_set(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.document_file.return_value = self.document_pk
        result = domain_services_accessor.document().document_file(
            file_content=b"",
            file_name="file_name.pdf",
            document_name="document_name",
            source=None,
            run_pipeline=False,
            llm_type=None,
            language="eng",
            engine="TESSERACT",
            tenant=str(uuid.uuid4()),
            extraction_params={},
        )

        assert result == self.document_pk
        document_access_manager_mock.add_permissions_after_creating.assert_called_with(self.document_pk)

    def test_extract_data__user_has_access__data_extracted(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        documents = [self.document_entity]
        document_service_mock.extract_data.return_value = documents
        result = domain_services_accessor.document().extract_data([self.document_pk])

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_get__user_has_access__success(self, document_service_mock, document_access_manager_mock, domain_services_accessor):
        document_service_mock.get.return_value = self.document_entity
        result = domain_services_accessor.document().get(self.document_pk)

        assert isinstance(result, DocumentEntity)
        document_access_manager_mock.check_is_accessible_read.assert_called_with([self.document_pk])

    def test_get_descendants__user_has_access__success(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_entity_descendant = DocumentEntityFactory(parent_id=self.document_pk)
        document_service_mock.get_descendants.return_value = [document_entity_descendant]
        result = domain_services_accessor.document().get_descendants(self.document_pk)

        assert result == [document_entity_descendant]
        document_access_manager_mock.check_is_accessible_read.assert_called_with([self.document_pk])

    def test_get_document_files__user_has_access__success(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.get_document_files.return_value = DocumentFilesDataFactory()
        result = domain_services_accessor.document().get_document_files(self.document_pk)

        assert isinstance(result, DocumentFilesDataObject)
        document_access_manager_mock.check_is_accessible_read.assert_called_with([self.document_pk])

    def test_get_document_list__user_has_access__success(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        filter_object = DocumentListFilterObject()
        result = domain_services_accessor.document().get_document_list(filter_object)

        assert isinstance(result, DocumentListDataObject)
        document_access_manager_mock.patch_filter.assert_called_with(filter_object)

    def test_get_processed_images__user_has_access__success(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.get_processed_images.return_value = DocumentFilesDataFactory()
        result = domain_services_accessor.document().get_processed_images(self.document_pk)

        assert isinstance(result, DocumentFilesDataObject)
        document_access_manager_mock.check_is_accessible_read.assert_called_with([self.document_pk])

    def test_identify__user_has_access__identified(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.identify.return_value = [self.document_entity]
        result = domain_services_accessor.document().identify([self.document_pk])

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_remove_label__user_has_access__label_removed(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.remove_label.return_value = True
        result = domain_services_accessor.document().remove_label(document_entity_pk=self.document_pk, label_pk="1")

        assert result is True
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_upsert_document_metadata__user_has_access__added(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor, document_metadata
    ):
        document_service_mock.upsert_document_metadata.return_value = document_metadata
        added_metadata = domain_services_accessor.document().upsert_document_metadata(document_metadata)

        assert added_metadata == document_metadata
        document_access_manager_mock.check_is_accessible_write.assert_called_with([document_metadata.document_id])

    def test_get_document_metadata__user_has_access__success(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor, document_metadata
    ):
        document_service_mock.get_document_metadata.return_value = document_metadata
        metadata = domain_services_accessor.document().get_document_metadata(document_metadata.document_id)

        assert metadata == document_metadata
        document_access_manager_mock.check_is_accessible_read.assert_called_with([document_metadata.document_id])

    def test_delete_document_metadata__user_has_access__deleted(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor, document_metadata
    ):
        document_service_mock.delete_document_metadata.return_value = None
        domain_services_accessor.document().delete_document_metadata(document_metadata)

        document_access_manager_mock.check_is_accessible_write.assert_called_with([document_metadata.document_id])

    def test_reset_reviewer__user_has_access__reset(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.reset_reviewer.return_value = [self.document_entity]
        result = domain_services_accessor.document().reset_reviewer([self.document_pk])

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_retry_last_step__user_has_access__retried(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.retry_last_step.return_value = self.document_entity
        result = domain_services_accessor.document().retry_last_step(self.document_pk)

        assert isinstance(result, DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_run_pipeline__user_has_access__run(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.run_pipeline.return_value = [self.document_entity]
        result = domain_services_accessor.document().run_pipeline(document_entity_pks=[self.document_pk], engine="TESSERACT")

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_run_pipeline_from_step__user_has_access__run(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.run_pipeline_from_step.return_value = [self.document_entity]
        result = domain_services_accessor.document().run_pipeline_from_step(
            document_entity_pks=[self.document_pk], step=PipelineStepsEnum.EXTRACTION, language="eng"
        )

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_start_review__user_has_access__started(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.start_review.return_value = [self.document_entity]
        result = domain_services_accessor.document().start_review(document_entity_pks=[self.document_pk])

        assert isinstance(result[0], DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_update__user_has_access__updated(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document = self.document_entity
        document_service_mock.update.return_value = self.document_pk
        result = domain_services_accessor.document().update(document)

        assert result == self.document_pk
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_partially_update__user_has_access__updated(
        self, document_service_mock, document_access_manager_mock, domain_services_accessor
    ):
        document_service_mock.partially_update.return_value = self.document_entity
        result = domain_services_accessor.document().partially_update(
            document_entity_pk=self.document_pk, document_fields={"field": "value"}
        )

        assert isinstance(result, DocumentEntity)
        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])

    def test_update_priorities__user_has_access__updated(self, domain_services_accessor):
        with pytest.raises(NotImplementedError):
            domain_services_accessor.document().update_priorities()

    def test_validate__accessor_called(self, domain_services_accessor, document_service_mock, document_access_manager_mock):
        domain_services_accessor.document().validate(self.document_pk)

        document_access_manager_mock.check_is_accessible_write.assert_called_with([self.document_pk])
        document_service_mock.validate.assert_called_with(self.document_pk)
