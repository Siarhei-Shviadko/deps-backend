class TestCaseBatchUpload:
    def test__create_batch_id__return_batch_id(self, repositories):
        batch_upload_repository = repositories.batch_upload_data()
        batch_id = batch_upload_repository.create_batch_id()

        assert batch_id

    def test__exists_batch_id__correct_batch_id(self, repositories):
        batch_upload_repository = repositories.batch_upload_data()
        batch_id = batch_upload_repository.create_batch_id()

        assert batch_upload_repository.exists_batch_id(batch_id)

    def test__exists_batch_id__incorrect_batch_id(self, repositories):
        batch_upload_repository = repositories.batch_upload_data()

        assert not batch_upload_repository.exists_batch_id("some_non_existing_batch_id")

    def test__fresh_batch_id_has_empty_data(self, repositories):
        batch_upload_repository = repositories.batch_upload_data()
        batch_id = batch_upload_repository.create_batch_id()
        batch_upload_data = batch_upload_repository.get_batch_upload_data(batch_id)

        assert not len(batch_upload_data)

    def test__update_batch_upload_data(self, repositories):
        batch_upload_repository = repositories.batch_upload_data()
        batch_id = batch_upload_repository.create_batch_id()

        batch_upload_data = {"document_id": "1"}
        batch_upload_repository.update_batch_upload_data(batch_id, batch_upload_data)

        assert batch_upload_repository.get_batch_upload_data(batch_id) == batch_upload_data
