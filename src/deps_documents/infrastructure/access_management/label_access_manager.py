from abc import ABC, abstractmethod
from typing import Callable, List

from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities import LabelEntityPk
from deps_documents.domain.exceptions import ForbiddenError, LabelAlreadyExistsError
from deps_documents.domain.interfaces import IDocumentUnitOfWork
from deps_documents.infrastructure.access_management.mixins import CurrentUserMixin


class ILabelServiceAccessManager(ABC):
    @abstractmethod
    def check_is_accessible_read(self, label_entity_pks: List[LabelEntityPk]) -> None:
        """
        This method should be implemented to check if user could read data from the Label
        """
        pass

    @abstractmethod
    def check_uniqueness(self, label_name: str) -> None:
        """
        This method should be implemented to check if Label name is unique
        """
        pass

    @abstractmethod
    def add_permissions_after_creating(self, label_entity_pk: LabelEntityPk) -> None:
        """
        This method should be implemented for some after entity creation logic. Fore example add label to user
        accessible labels list
        """
        pass

    @abstractmethod
    def patch_filter(self, options: LabelListFilterObject) -> None:
        """
        This method should be implemented to patch list filter object with proper values to restrict labels
        list fetching
        """
        pass


class LabelServiceAccessManagerTrap(ILabelServiceAccessManager):
    def check_is_accessible_read(self, label_entity_pks: List[LabelEntityPk]) -> None:
        pass

    def check_uniqueness(self, label_name: str) -> None:
        pass

    def add_permissions_after_creating(self, label_entity_pk: LabelEntityPk) -> None:
        pass

    def patch_filter(self, options: LabelListFilterObject) -> None:
        pass


class OrganisationBasedLabelServiceAccessManager(ILabelServiceAccessManager, CurrentUserMixin):
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork]):
        self._uow = uow

    def check_is_accessible_read(self, label_entity_pks: List[LabelEntityPk]) -> None:
        self._check_permission(label_entity_pks)

    def check_uniqueness(self, label_name: str) -> None:
        with self._uow() as uow:
            label_pks = uow.label.get_organisation_label_entity_pks(
                self.current_user.organisation,
                LabelListFilterObject(name=label_name),
            )
            uow.commit()
        if label_pks:
            raise LabelAlreadyExistsError(f"Label {label_name} already exists.")

    def add_permissions_after_creating(self, label_entity_pk: LabelEntityPk) -> None:
        with self._uow() as uow:
            uow.label.add_label_to_organisation(
                label_entity_pk,
                self.current_user.organisation,
            )
            uow.commit()

    def patch_filter(self, options: LabelListFilterObject) -> None:
        with self._uow() as uow:
            label_pks = uow.label.get_organisation_label_entity_pks(
                self.current_user.organisation,
                LabelListFilterObject(),
            )
            uow.commit()
        options.pks = label_pks

    def _check_permission(self, label_entity_pks: List[LabelEntityPk]) -> None:
        with self._uow() as uow:
            label_pks = uow.label.get_organisation_label_entity_pks(
                self.current_user.organisation,
                LabelListFilterObject(),
            )
            uow.commit()
        if not all(pk in label_pks for pk in label_entity_pks):
            raise ForbiddenError(f"User has no access to labels: `{label_entity_pks}`")
