import secrets

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import DocumentListFilterObject
from deps_documents.domain.entities import LabelEntity
from tests.factories import DocumentEntityFactory


class TestDocumentSearch:
    def test_search__search_by_title__right_docs_are_found(self, uow):
        unique_title = secrets.token_hex(16)
        docs = (DocumentEntityFactory(title=unique_title), DocumentEntityFactory())
        for doc in docs:
            uow.document.add(doc)

        found_docs = uow.document.get_list_by_filter(DocumentListFilterObject(search=unique_title))

        assert len(found_docs) == 1
        assert found_docs[0].title == unique_title

    def test_search__search_by_engine__right_docs_are_found(self, uow):
        docs = (
            DocumentEntityFactory(engine="TESSERACT"),
            DocumentEntityFactory(title="test", engine="ABBYY"),
        )
        for doc in docs:
            uow.document.add(doc)

        found_docs = uow.document.get_list_by_filter(DocumentListFilterObject(search="tesseract"))

        assert len(found_docs) == 1
        assert found_docs[0].engine == "TESSERACT"

    def test_search__search_by_state__right_docs_are_found(self, uow):
        docs = (
            DocumentEntityFactory(state=DocumentStateEnum.COMPLETED),
            DocumentEntityFactory(title="test", state=DocumentStateEnum.PREPROCESSING),
        )
        for doc in docs:
            uow.document.add(doc)

        found_docs = uow.document.get_list_by_filter(DocumentListFilterObject(search="ready"))

        assert len(found_docs) == 1
        assert found_docs[0].state == DocumentStateEnum.COMPLETED

    def test_search__search_by_label__right_docs_returned(self, uow):
        unique_label = secrets.token_hex(16)
        doc = uow.document.add(DocumentEntityFactory())
        uow.document.add(DocumentEntityFactory())

        label = uow.label.add(LabelEntity(name=unique_label))
        uow.document.add_label(label.pk, [doc.pk])

        found_docs = uow.document.get_list_by_filter(DocumentListFilterObject(search=unique_label))

        assert len(found_docs) == 1
        assert found_docs[0].pk == doc.pk
        assert found_docs[0].labels[0].name == unique_label

    def test_search__document_ids_are_specified__search_applied_only_to_docs_with_these_ids(self, uow):
        name = "test"
        doc = uow.document.add(DocumentEntityFactory(title=name))
        uow.document.add(DocumentEntityFactory(title=name))

        found_docs = uow.document.get_list_by_filter(DocumentListFilterObject(search=name, ids=[doc.pk]))

        assert len(found_docs) == 1
        assert found_docs[0].pk == doc.pk
