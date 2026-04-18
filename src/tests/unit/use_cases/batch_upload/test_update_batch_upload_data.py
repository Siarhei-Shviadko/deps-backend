from deps_documents.domain.exceptions import BatchIdNotFoundError


class TestUpdateBatchUploadUseCase:
    def test_execute_valid_batch_id(self, use_cases, repositories):
        repositories.batch_upload_data().update_batch_upload_data.return_value = {"test": "dict"}

        use_case = use_cases.update_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id="test_batch_id", batch_upload_data={"test": "dict"}))

        assert use_case_response.value.status

    def test_execute_invalid_batch_id(self, use_cases, repositories):
        repositories.batch_upload_data().update_batch_upload_data.side_effect = BatchIdNotFoundError

        use_case = use_cases.update_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id="test_batch_id", batch_upload_data={"test": "dict"}))

        assert use_case_response.error is not None
