import pytest

from deps_documents.domain.exceptions import ForbiddenError
from tests.factories import LabelEntityFactory


@pytest.fixture
def org_access_manager(label_service_access_manager):
    return label_service_access_manager.organisation()


@pytest.fixture
def label_fixture(uow):
    return uow.label.add(LabelEntityFactory())


@pytest.mark.usefixtures("enable_authorization_for_container", "set_test_user")
class TestOrganisationBasedLabelServiceAccessManager:
    def test__check_permission__positive(self, org_access_manager, uow, label_fixture, user_fixture):
        uow.label.add_label_to_organisation(label_fixture.pk, user_fixture["groups"][0])
        org_access_manager._check_permission([label_fixture.pk])

    def test__check_permission__no_permission(self, org_access_manager, label_fixture):
        with pytest.raises(ForbiddenError):
            org_access_manager._check_permission([label_fixture.pk])
