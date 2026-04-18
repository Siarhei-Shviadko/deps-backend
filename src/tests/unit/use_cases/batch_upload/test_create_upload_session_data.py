class TestCreateUploadSessionDataUseCase:
    def test_execute_batch_id_created(self, use_cases, repositories):
        repositories.batch_upload_data().create_batch_id.return_value = "test_string"

        use_case = use_cases.create_upload_session()
        use_case_response = use_case.execute()

        assert use_case_response.value.batch_id == "test_string"
