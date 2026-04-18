from typing import Callable, List

from deps_documents.domain.dtos import (
    DocumentTypeChangeAggregation,
    DocumentTypeChangeFilter,
)
from deps_documents.domain.interfaces import IDocumentUnitOfWork


class AnalyticsService:
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork]):
        self._uow = uow

    def aggregate_document_type_change(self, options: DocumentTypeChangeFilter) -> List[DocumentTypeChangeAggregation]:
        with self._uow() as uow:
            document_type_changes = uow.analytics.get_document_type_changes(options)
            uow.commit()
        return document_type_changes
