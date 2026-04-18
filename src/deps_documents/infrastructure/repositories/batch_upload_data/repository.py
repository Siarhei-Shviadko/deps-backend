import json
from datetime import timedelta
from typing import Dict
from uuid import uuid4

import redis

from deps_documents.domain.exceptions import BatchIdNotFoundError
from deps_documents.domain.interfaces import IBatchUploadDataRepository


class BatchUploadDataRepository(IBatchUploadDataRepository):
    def __init__(self, host: str, port: int, db: int, password: str) -> None:
        self._storage = redis.Redis(host=host, port=port, db=db, password=password)

    def create_batch_id(self) -> str:
        batch_id = str(uuid4())
        batch_id_key = self._get_key_from_batch_id(batch_id)
        self._storage.setex(batch_id_key, timedelta(days=1), json.dumps({}))

        return batch_id

    def exists_batch_id(self, batch_id: str) -> bool:
        batch_id_key = self._get_key_from_batch_id(batch_id)
        return self._storage.exists(batch_id_key) > 0

    def get_batch_upload_data(self, batch_id: str) -> Dict[str, str]:
        if not self.exists_batch_id(batch_id):
            raise BatchIdNotFoundError()

        batch_id_key = self._get_key_from_batch_id(batch_id)
        return json.loads(self._storage.get(batch_id_key))

    def update_batch_upload_data(self, batch_id: str, upload_data: Dict[str, str]) -> None:
        if not self.exists_batch_id(batch_id):
            raise BatchIdNotFoundError()

        batch_id_key = self._get_key_from_batch_id(batch_id)
        self._storage.setex(batch_id_key, timedelta(days=1), json.dumps(upload_data))

    @staticmethod
    def _get_key_from_batch_id(batch_id: str) -> str:
        return "".join(["upload_batch_id_", batch_id])
