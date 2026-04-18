from deps_documents.domain.constants import SKIP_VALIDATION_STATES
from deps_documents.domain.entities import DocumentEntity


class CanValidationBeSkipped:
    @staticmethod
    def is_satisfied_by(doc_entity: DocumentEntity) -> bool:
        return doc_entity.state in SKIP_VALIDATION_STATES
