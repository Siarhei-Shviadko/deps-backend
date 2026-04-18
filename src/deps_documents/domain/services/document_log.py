from datetime import datetime
from typing import Callable, List

from deps_documents.domain.constants import DocumentLogEnum, DocumentStateEnum
from deps_documents.domain.entities import (
    DocumentEntityPk,
    DocumentLogEntity,
    StateInterval,
)
from deps_documents.domain.exceptions import DocumentStateError
from deps_documents.domain.interfaces import IDocumentUnitOfWork


class DocumentLogService:
    enum_str2enum_state_mapper = {str(state): state for state in DocumentStateEnum}

    def __init__(self, unit_of_work: Callable[..., IDocumentUnitOfWork]):
        self._uow = unit_of_work

    def get_document_time_state_intervals(self, document_id: DocumentEntityPk) -> List[StateInterval]:
        with self._uow() as uow:
            document = uow.document.get(document_id)
            document_logs = self._get_document_state_changing_logs(document_id)
            document_logs = sorted(document_logs, key=lambda log: log.created_at)
            uow.commit()

        intervals = [
            StateInterval(
                state=DocumentStateEnum.NEW,
                start_time=document.date,
                finish_time=document_logs[0].created_at,
            ),
        ]

        for prev_log, cur_log in zip(document_logs[:-1], document_logs[1:]):
            start_time = prev_log.created_at
            finish_time = cur_log.created_at
            state = cur_log.previous

            interval = StateInterval(
                state=self._convert_str_to_state(state),
                start_time=start_time,
                finish_time=finish_time,
            )
            intervals.append(interval)

        intervals.append(
            StateInterval(
                state=self._convert_str_to_state(document_logs[-1].current),
                start_time=document_logs[-1].created_at,
                finish_time=datetime.now(),
            ),
        )

        return intervals

    def _get_document_state_changing_logs(self, document_id: DocumentEntityPk) -> List[DocumentLogEntity]:
        with self._uow() as uow:
            document_logs = uow.document_log.get_document_logs(document_id)
            uow.commit()
        return [log for log in document_logs if log.action == DocumentLogEnum.STATE_CHANGED]

    @staticmethod
    def _convert_str_to_state(value: str) -> DocumentStateEnum:
        if value not in DocumentLogService.enum_str2enum_state_mapper:
            raise DocumentStateError

        return DocumentLogService.enum_str2enum_state_mapper[value]
