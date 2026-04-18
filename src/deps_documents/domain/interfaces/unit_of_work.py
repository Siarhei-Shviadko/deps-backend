from abc import abstractmethod
from typing import Callable

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_documents.domain.domain_event import DomainEvent
from deps_documents.domain.interfaces import (
    IAnalyticsRepository,
    ICommentRepository,
    IDocumentEntityRepository,
    IDocumentLogRepository,
    IDocumentTypeRepository,
    IGroupRepository,
    ILabelRepository,
    IRelationRepository,
)
from deps_documents.extras.datasource import Database
from deps_documents.extras.unit_of_work import IUoW


class IDocumentUnitOfWork(IUoW):
    @abstractmethod
    def __init__(
        self,
        database: Database,
        event_publisher: DomainEventPublisher,
        comment_repo_factory: Callable[..., ICommentRepository],
        document_repo_factory: Callable[..., IDocumentEntityRepository],
        document_log_repo_factory: Callable[..., IDocumentLogRepository],
        analytics_repo_factory: Callable[..., IAnalyticsRepository],
        label_repo_factory: Callable[..., ILabelRepository],
        relation_repo_factory: Callable[..., IRelationRepository],
        document_type_repo_factory: Callable[..., IDocumentTypeRepository],
    ):
        pass

    @property
    @abstractmethod
    def comment(self) -> ICommentRepository:
        pass

    @property
    @abstractmethod
    def document(self) -> IDocumentEntityRepository:
        pass

    @property
    @abstractmethod
    def document_log(self) -> IDocumentLogRepository:
        pass

    @property
    @abstractmethod
    def analytics(self) -> IAnalyticsRepository:
        pass

    @property
    @abstractmethod
    def label(self) -> ILabelRepository:
        pass

    @property
    @abstractmethod
    def relation(self) -> IRelationRepository:
        pass

    @property
    @abstractmethod
    def document_type(self) -> IDocumentTypeRepository:
        pass

    @property
    @abstractmethod
    def group(self) -> IGroupRepository:
        pass

    @abstractmethod
    def add_events(self, events: list[DomainEvent]) -> None:
        pass
