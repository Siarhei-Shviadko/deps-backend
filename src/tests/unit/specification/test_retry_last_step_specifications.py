import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.specifications import (
    CanBeRetried,
    CanBeRetriedExtraction,
    CanBeRetriedIdentification,
    CanBeRetriedPreprocessing,
)
from tests.factories import DocumentEntityFactory
from tests.factories.document_entity import ErrorEntityFactory


class TestCaseRetrySpecifications:
    @pytest.mark.parametrize(
        "test_error,expected", [(error, expected) for error, expected in ((ErrorEntityFactory, True), (None, False))]
    )
    def test_is_satisfied_for_retry__many_states__return_expected(self, test_error, expected):
        document = DocumentEntityFactory(error=test_error)
        response = CanBeRetried.is_satisfied_by(document)

        assert response == expected

    @pytest.mark.parametrize(
        "test_state,expected", [(state, state == DocumentStateEnum.DATA_EXTRACTION) for state in DocumentStateEnum]
    )
    def test_is_satisfied_for_retry_extraction__many_states__return_expected(self, test_state, expected):
        document = DocumentEntityFactory(error=ErrorEntityFactory(in_state=test_state))
        response = CanBeRetriedExtraction.is_satisfied_by(document)

        assert response == expected

    @pytest.mark.parametrize(
        "test_state,expected", [(state, state == DocumentStateEnum.IDENTIFICATION) for state in DocumentStateEnum]
    )
    def test_is_satisfied_for_retry_identification__many_states__return_expected(self, test_state, expected):
        document = DocumentEntityFactory(error=ErrorEntityFactory(in_state=test_state))
        response = CanBeRetriedIdentification.is_satisfied_by(document)

        assert response == expected

    @pytest.mark.parametrize(
        "test_state,expected", [(state, state == DocumentStateEnum.PREPROCESSING) for state in DocumentStateEnum]
    )
    def test_is_satisfied_for_retry_preprocess__many_states__return_expected(self, test_state, expected):
        document = DocumentEntityFactory(error=ErrorEntityFactory(in_state=test_state))
        response = CanBeRetriedPreprocessing.is_satisfied_by(document)

        assert response == expected
