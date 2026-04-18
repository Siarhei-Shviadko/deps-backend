import threading
from typing import Callable
from uuid import uuid4

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_documents import constants
from deps_documents.domain.domain_event import DomainEvent
from deps_documents.domain.interfaces import (
    IAnalyticsRepository,
    ICommentRepository,
    IDocumentEntityRepository,
    IDocumentLogRepository,
    IDocumentTypeRepository,
    IDocumentUnitOfWork,
    IGroupRepository,
    ILabelRepository,
    IRelationRepository,
)
from deps_documents.extras.datasource import Database


class DocumentUnitOfWork(IDocumentUnitOfWork):
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
        group_repo_factory: Callable[..., IGroupRepository],
    ):
        self._event_publisher = event_publisher
        self._comment_repo_factory = comment_repo_factory
        self._document_repo_factory = document_repo_factory
        self._document_log_repo_factory = document_log_repo_factory
        self._analytics_repo_factory = analytics_repo_factory
        self._label_repo_factory = label_repo_factory
        self._relation_repo_factory = relation_repo_factory
        self._document_type_repo_factory = document_type_repo_factory
        self._group_repo_factory = group_repo_factory

        self._database = database

        self._registry = threading.local()
        self._events: list[DomainEvent] = []

    @property
    def document(self) -> IDocumentEntityRepository:
        return self._document_repo_factory(self._connection)

    @property
    def document_log(self) -> IDocumentLogRepository:
        return self._document_log_repo_factory(self._connection)

    @property
    def analytics(self) -> IAnalyticsRepository:
        return self._analytics_repo_factory(self._connection)

    @property
    def label(self) -> ILabelRepository:
        return self._label_repo_factory(self._connection)

    @property
    def relation(self) -> IRelationRepository:
        return self._relation_repo_factory(self._connection)

    @property
    def comment(self) -> ICommentRepository:
        return self._comment_repo_factory(self._connection)

    @property
    def document_type(self) -> IDocumentTypeRepository:
        return self._document_type_repo_factory(self._connection)

    @property
    def group(self) -> IGroupRepository:
        return self._group_repo_factory(self._connection)

    def rollback(self) -> None:
        self._transaction.rollback()
        self._transaction.close()

    def commit(self) -> None:
        self._transaction.commit()
        self._publish_events()

    def add_events(self, events: list[DomainEvent]) -> None:
        self._events.extend(events)

    def open_transaction(self):
        self._initialize_connection()
        self._start_transaction()

    def close_transaction(self):
        self.rollback()

    def __enter__(self):
        self.open_transaction()
        return self

    @property
    def _transaction(self):
        return self._registry.transaction

    @_transaction.setter
    def _transaction(self, transaction):
        self._registry.transaction = transaction

    def _initialize_connection(self):
        self._connection = self._database.get_connection()

    def _start_transaction(self):
        """
        .begin_nested() deprecated since SQLAlchemy 1.4
        For SQLAlchemy 1.4+ use code below:
        self._transaction = self._connection.get_transaction() if self._connection.in_transaction() else self._connection.begin()
        """
        self._transaction = self._connection.begin_nested()

    def _publish_events(self):
        self._event_publisher.publish(constants.DOCUMENTS_EXCHANGER, "None", self._events, headers={"ID": uuid4().hex})
        self._events.clear()
