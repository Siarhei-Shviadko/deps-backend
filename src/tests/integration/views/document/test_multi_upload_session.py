from contextlib import contextmanager
from io import BytesIO
from threading import Thread
from time import sleep
from timeit import default_timer
from typing import List

import pytest

NUM_FILES_PER_DOCUMENT = 5
FILE_SAVING_TIME = 0.05


class DocumentServiceStub:
    def __init__(self, processing_time: float) -> None:
        self._count = 1
        self._processing_time = processing_time

    def add_file(self, *args, document_entity_pk: int, **kwargs) -> int:
        sleep(self._processing_time)

        return document_entity_pk

    def document_file(self, *args, **kwargs) -> int:
        res = self._count
        self._count += 1

        sleep(self._processing_time)

        return res


def timeit(f, *args, **kwargs) -> float:
    with timeit_context() as measures:
        f(*args, **kwargs)
    start_t, stop_t = measures

    return stop_t - start_t


@contextmanager
def timeit_context():
    measures: List[float] = []
    stop_t, start_t = None, None
    try:
        start_t = default_timer()
        yield measures
    finally:
        stop_t = default_timer()
        measures.extend([start_t, stop_t])


@pytest.fixture
def stub_document_service(domain_services):
    document_stub = DocumentServiceStub(processing_time=FILE_SAVING_TIME)
    with domain_services.document.override(document_stub):
        yield


class TestMultiUploadSessionView:
    def test_post__multi_upload_session__return_200(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")

        assert response.status_code == 200

    @pytest.mark.usefixtures("stub_document_service")
    def test_post__multi_upload_files__synchronized(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")
        batch_id = response.json()["batchId"]

        document_ids = []

        num_files = NUM_FILES_PER_DOCUMENT
        ts = [
            Thread(
                target=upload_file,
                args=(
                    client,
                    batch_id,
                    document_ids,
                ),
            )
            for _ in range(num_files)
        ]

        with timeit_context() as measures:
            for t in ts:
                t.start()

            for t in ts:
                t.join()

        start_t, stop_t = measures
        exec_time = stop_t - start_t

        theory_min_exec_time = FILE_SAVING_TIME * NUM_FILES_PER_DOCUMENT

        assert len(set(document_ids)) == 1
        assert theory_min_exec_time * 0.95 < exec_time

    @pytest.mark.usefixtures("stub_document_service")
    def test_post__multi_upload_files__dont_block_other(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")
        batch_id1 = response.json()["batchId"]
        response = client.post("/api/document/v1/documents/multi-upload-session")
        batch_id2 = response.json()["batchId"]

        document_ids = []

        num_files = NUM_FILES_PER_DOCUMENT
        ts = [
            Thread(
                target=upload_file,
                args=(
                    client,
                    batch_id1,
                    document_ids,
                ),
            )
            for _ in range(num_files)
        ]

        with timeit_context() as measures:
            for t in ts:
                t.start()

            exec_time = timeit(upload_file, client, batch_id2, document_ids)

            for t in ts:
                t.join()

        start_t, stop_t = measures
        total_exec_time = stop_t - start_t

        theory_min_exec_time = FILE_SAVING_TIME * NUM_FILES_PER_DOCUMENT
        overhead_exec_time = total_exec_time - theory_min_exec_time
        theory_max_exec_time = FILE_SAVING_TIME + overhead_exec_time

        assert len(set(document_ids)) == 2
        assert exec_time < 1.05 * theory_max_exec_time

    @pytest.mark.usefixtures("stub_document_service")
    def test_post__multi_upload_files__no_dead_locks(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")
        batch_id1 = response.json()["batchId"]
        response = client.post("/api/document/v1/documents/multi-upload-session")
        batch_id2 = response.json()["batchId"]

        batch_ids = [batch_id1, batch_id2]

        document_ids = []

        num_files = NUM_FILES_PER_DOCUMENT * 2
        ts = [
            Thread(
                target=upload_file,
                args=(
                    client,
                    batch_ids[i % 2],
                    document_ids,
                ),
            )
            for i in range(num_files)
        ]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

        assert len(set(document_ids)) == 2


def upload_file(client, batch_id: str, result_ids: List[int]) -> None:
    with BytesIO(b"a new document file content") as f:
        dfile = {
            "file": ("document_file.jpg", f, "application/jpg"),
        }
        data = {
            "runPipeline": False,
            "batchId": batch_id,
        }

        response = client.post(
            "/api/document/v1/documents/document-file",
            files=dfile,
            data=data,
        )

    document_id = response.json()["id"]
    result_ids.append(document_id)
