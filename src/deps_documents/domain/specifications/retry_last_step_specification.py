from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import DocumentEntity


class CanBeRetried:
    @staticmethod
    def is_satisfied_by(document: DocumentEntity):
        return bool(document.error and document.error.in_state)


class CanBeRetriedExtraction:
    @staticmethod
    def is_satisfied_by(document: DocumentEntity):
        return document.error.in_state == DocumentStateEnum.DATA_EXTRACTION


class CanBeRetriedIdentification:
    @staticmethod
    def is_satisfied_by(document: DocumentEntity):
        return document.error.in_state == DocumentStateEnum.IDENTIFICATION


class CanBeRetriedPreprocessing:
    @staticmethod
    def is_satisfied_by(document: DocumentEntity):
        return document.error.in_state == DocumentStateEnum.PREPROCESSING
