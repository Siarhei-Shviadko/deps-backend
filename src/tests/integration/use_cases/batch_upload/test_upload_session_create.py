class TestCreateUploadSessionUseCase:
    def test__create_batch_id__return_batch_id(self, use_cases):
        use_case = use_cases.create_upload_session()
        use_case_response = use_case.execute()

        assert use_case_response.value.batch_id
