from abc import ABC, abstractmethod

from deps_documents.domain.constants import DocumentPriorityEnum
from deps_documents.domain.entities import DocumentEntity


class IPriorityManager(ABC):
    @abstractmethod
    def get_priority(self, document_entity: DocumentEntity) -> DocumentPriorityEnum:
        """
        Calculates document priority based on some domain logic
        """
        pass
