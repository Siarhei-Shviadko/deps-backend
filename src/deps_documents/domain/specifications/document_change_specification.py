from deps_documents.domain.constants import PROCESSING_STATES, DocumentStateEnum
from deps_documents.domain.entities import DocumentEntity


class CanBeChangedSpecification:
    @staticmethod
    def is_satisfied_by(doc_entity: DocumentEntity) -> bool:
        return doc_entity.state not in PROCESSING_STATES and doc_entity.state != DocumentStateEnum.NEW
