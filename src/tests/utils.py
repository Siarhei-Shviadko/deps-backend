from deps_documents.domain.constants import ContainerTypesEnum
from tests.factories import DocumentEntityFactory
from tests.factories.document_entity import ContainerEmailMetadataFactory


class ContainerDocumentCreatorMixin:
    @staticmethod
    def _create_email_container_doc(uow, parent_doc=None, child_docs=None, child_docs_number=3):
        if parent_doc is None:
            parent_doc = uow.document.add(
                DocumentEntityFactory(container_type=ContainerTypesEnum.EMAIL, container_metadata=ContainerEmailMetadataFactory())
            )
        if child_docs is None:
            child_docs = [uow.document.add(DocumentEntityFactory(parent_id=parent_doc.pk)) for _ in range(child_docs_number)]

        return parent_doc, child_docs
