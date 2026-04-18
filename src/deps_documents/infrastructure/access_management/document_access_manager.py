from abc import ABC, abstractmethod
from typing import Callable, List

from deps_documents.domain.dtos import DocumentListFilterObject, LabelListFilterObject
from deps_documents.domain.entities import DocumentEntityPk, LabelEntityPk
from deps_documents.domain.exceptions import (
    DocumentForbiddenError,
    DocumentNotFoundError,
    ForbiddenError,
)
from deps_documents.domain.interfaces import IDocumentUnitOfWork
from deps_documents.infrastructure.access_management.mixins import CurrentUserMixin


class IDocumentServiceAccessManager(ABC):
    @abstractmethod
    def check_is_accessible_create(self) -> None:
        """
        This method should be implemented to check if user could create a new Document Entity. If there is no access
        should raise `ForbiddenError`. Call `add_permissions_after_creating` after Entity creation
        """
        pass

    @abstractmethod
    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        """
        This method should be implemented to check if user could read data from the Document, including exports and
        document images, pdf-files, email etc. If there is no access should raise `ForbiddenError`
        """
        pass

    @abstractmethod
    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        """
        This method should be implemented to check if user could mutate the Document, including sending to extraction,
        making complete_review, changing document type, language, extracted_data, etc. If there is no access
        should raise `ForbiddenError`
        """
        pass

    @abstractmethod
    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        """
        This method should be implemented for some after entity creation logic. Fore example add document to user
        accessible documents list
        """
        pass

    @abstractmethod
    def patch_filter(self, options: DocumentListFilterObject) -> None:
        """
        This method should be implemented to patch list filter object with proper values to restrict documents
        list fetching
        """
        pass

    @abstractmethod
    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        """
        This method should be implemented to check if user could add the specified labels to a document.
        If the user does not have access to one or more labels, should raise `ForbiddenError`.
        """
        pass


class DocumentServiceAccessManagerTrap(IDocumentServiceAccessManager):
    def check_is_accessible_create(self) -> None:
        pass

    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        pass

    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        pass

    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        pass

    def patch_filter(self, options: DocumentListFilterObject) -> None:
        pass

    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        pass


class UserBasedDocumentServiceAccessManager(IDocumentServiceAccessManager, CurrentUserMixin):
    def __init__(self, unit_of_work: Callable[..., IDocumentUnitOfWork]):
        self._uow = unit_of_work

    def check_is_accessible_create(self) -> None:
        pass

    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_is_accessible_for_user(document_entity_pks)

    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_is_accessible_for_user(document_entity_pks)

    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        with self._uow() as uow:
            uow.document.add_document_to_user(document_entity_pk, self.current_user.subject)
            uow.commit()

    def patch_filter(self, options: DocumentListFilterObject) -> None:
        with self._uow() as uow:
            user_docs = uow.document.get_user_document_entity_pks(self.current_user.subject)
            uow.commit()
        options.ids = user_docs

    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        pass

    def _check_is_accessible_for_user(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        with self._uow() as uow:
            user_document_pks = uow.document.get_user_document_entity_pks(self.current_user.subject)
            uow.commit()
        if not all(pk in user_document_pks for pk in document_entity_pks):
            raise DocumentForbiddenError(f"User has no access to documents: `{document_entity_pks}`")


class RoleBasedDocumentServiceAccessManager(IDocumentServiceAccessManager, CurrentUserMixin):
    def __init__(self, create_role: str, read_role: str, write_role: str):
        self._create_role = create_role
        self._read_role = read_role
        self._write_role = write_role

    def check_is_accessible_create(self) -> None:
        if self._create_role in self.current_user.roles:
            return
        raise DocumentForbiddenError("User has no access for creating documents")

    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        if self._read_role in self.current_user.roles:
            return
        raise DocumentForbiddenError("User has no access for reading documents")

    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        if self._write_role in self.current_user.roles:
            return
        raise DocumentForbiddenError("User has no access for managing document")

    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        pass

    def patch_filter(self, options: DocumentListFilterObject) -> None:
        pass

    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        pass


class GroupBasedDocumentServiceAccessManager(IDocumentServiceAccessManager, CurrentUserMixin):
    def __init__(self, unit_of_work: Callable[..., IDocumentUnitOfWork], admins_group: str):
        self._uow = unit_of_work
        self._admins = admins_group

    def check_is_accessible_create(self) -> None:
        pass

    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_is_accessible_for_user(document_entity_pks)

    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_is_accessible_for_user(document_entity_pks)

    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        with self._uow() as uow:
            uow.document.add_document_to_user(document_entity_pk, self.current_user.subject)
            uow.commit()

    def patch_filter(self, options: DocumentListFilterObject) -> None:
        if self._is_admin():
            return

        user_documents_pks = self._get_user_documents_pks()
        options.ids = user_documents_pks

    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        pass

    def _check_is_accessible_for_user(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        if self._is_admin():
            return

        user_documents_pks = self._get_user_documents_pks()
        if not all(pk in user_documents_pks for pk in document_entity_pks):
            raise DocumentForbiddenError(f"User has no access to documents: `{document_entity_pks}`")

    def _get_user_documents_pks(self):
        with self._uow() as uow:
            user_document_pks = uow.document.get_user_document_entity_pks(self.current_user.subject)
            uow.commit()
        return user_document_pks

    def _is_admin(self):
        return self._admins in self.current_user.groups


class OrganisationBasedDocumentServiceAccessManager(IDocumentServiceAccessManager, CurrentUserMixin):
    def __init__(self, unit_of_work: Callable[..., IDocumentUnitOfWork]):
        self._uow = unit_of_work

    def check_is_accessible_create(self) -> None:
        pass

    def check_is_accessible_read(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_permission(document_entity_pks)

    def check_is_accessible_write(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        self._check_permission(document_entity_pks)

    def add_permissions_after_creating(self, document_entity_pk: DocumentEntityPk) -> None:
        with self._uow() as uow:
            uow.document.add_document_to_user_and_organisation(
                document_entity_pk,
                self.current_user.subject,
                self.current_user.organisation,
            )
            uow.commit()

    def patch_filter(self, options: DocumentListFilterObject) -> None:
        with self._uow() as uow:
            documents_pks = uow.document.get_organisation_document_entity_pks(self.current_user.organisation)
            uow.commit()
        options.ids = documents_pks

    def check_can_add_labels(self, label_entity_pks: List[LabelEntityPk]) -> None:
        with self._uow() as uow:
            label_pks = uow.label.get_organisation_label_entity_pks(
                self.current_user.organisation,
                LabelListFilterObject(),
            )
            uow.commit()
        if not all(pk in label_pks for pk in label_entity_pks):
            raise ForbiddenError(f"User has no access to labels: `{label_entity_pks}`")

    def _check_permission(self, document_entity_pks: List[DocumentEntityPk]) -> None:
        if not document_entity_pks:
            return

        with self._uow() as uow:
            documents_exist = uow.document.check_documents_for_organisation(
                organisation_entity_name=self.current_user.organisation,
                document_ids=document_entity_pks,
            )
            if not documents_exist:
                raise DocumentNotFoundError(f"Document `{document_entity_pks[0]}` not found.")

            uow.commit()
