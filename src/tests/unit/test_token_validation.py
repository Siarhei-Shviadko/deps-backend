import pytest

from deps_documents.auth import is_user_has_one_organisation, validate_user_organisation
from deps_documents.domain.exceptions.common import ForbiddenError


def test__is_user_has_one_organisation__positive(valid_decoded_token):
    expected = True
    test_output = is_user_has_one_organisation(valid_decoded_token)

    assert expected == test_output


def test__is_user_has_one_organisation__negative(invalid_decoded_token):
    expected = False
    test_output = is_user_has_one_organisation(invalid_decoded_token)

    assert expected == test_output


def test__validate_user_organisation__positive(valid_decoded_token):
    validate_user_organisation(valid_decoded_token)


def test__validate_user_organisation__negative(invalid_decoded_token):
    with pytest.raises(ForbiddenError):
        validate_user_organisation(invalid_decoded_token)
