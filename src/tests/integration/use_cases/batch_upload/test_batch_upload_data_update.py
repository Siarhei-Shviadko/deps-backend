class TestCreateUploadSessionUseCase:
    def test__update_batch_upload_data(self, repositories, use_cases):
        batch_upload_repository = repositories.batch_upload_data()
        batch_id = batch_upload_repository.create_batch_id()
        batch_upload_data = {"document_id": "1"}

        use_case = use_cases.update_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id=batch_id, batch_upload_data=batch_upload_data))

        assert batch_upload_repository.get_batch_upload_data(batch_id) == batch_upload_data
        assert use_case_response.value.status

    def test__update_batch_upload_data_invalid_batch_id(self, repositories, use_cases):
        repositories.batch_upload_data().create_batch_id()

        use_case = use_cases.update_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id="10", batch_upload_data={"document_id": "1"}))

        assert use_case_response.error is not None
