class TestGetBatchUploadDataUseCase:
    def test__fresh_batch_id_has_empty_data(self, repositories, use_cases):
        batch_upload_dao = repositories.batch_upload_data()
        batch_id = batch_upload_dao.create_batch_id()
        use_case = use_cases.get_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id=batch_id))

        assert not len(use_case_response.value.batch_upload_data)

    def test__invalid_batch_id(self, use_cases):
        use_case = use_cases.get_batch_upload_data()
        use_case_response = use_case.execute(use_case.Request(batch_id="test"))

        assert use_case_response.error is not None
