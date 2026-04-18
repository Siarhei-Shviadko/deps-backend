from deps_documents.domain.entities import DocumentEntity


class NeedDissectionSpecification:
    @staticmethod
    def is_satisfied_by(doc_entity: DocumentEntity) -> bool:
        return doc_entity.container_type is not None
