from itertools import chain

from tests.utils import ContainerDocumentCreatorMixin


class TestDocumentEntityRepositoryGetChildDocs(ContainerDocumentCreatorMixin):
    def test_get_child_docs__doc_with_one_level_childs__return_childs_list(self, uow):
        parent_doc, child_docs = self._create_email_container_doc(uow)

        res_child_docs = uow.document.get_descendants(parent_doc.pk)

        assert sorted(res_child_docs, key=lambda x: x.pk) == sorted(child_docs, key=lambda x: x.pk)

    def test_get_child_docs__doc_with_two_level_container_childs__return_childs_list(self, uow):
        first_level_parent, first_level_childs = self._create_email_container_doc(uow)
        second_level_parent, second_level_childs = self._create_email_container_doc(uow, parent_doc=first_level_childs[0])

        res_child_docs = uow.document.get_descendants(first_level_parent.pk)

        assert sorted(res_child_docs, key=lambda x: x.pk) == sorted(
            chain(second_level_childs, first_level_childs[1:]), key=lambda x: x.pk
        )

    def test_get_child_docs__doc_with_three_level_container_childs__return_childs_list(self, uow):
        first_level_parent, first_level_childs = self._create_email_container_doc(uow)
        second_level_parent, second_level_childs = self._create_email_container_doc(uow, parent_doc=first_level_childs[0])
        third_level_parent, third_level_childs = self._create_email_container_doc(uow, parent_doc=second_level_childs[0])

        res_child_docs = uow.document.get_descendants(first_level_parent.pk)

        assert sorted(res_child_docs, key=lambda x: x.pk) == sorted(
            chain(first_level_childs[1:], second_level_childs[1:], third_level_childs), key=lambda x: x.pk
        )

    def test_get_child_docs__doc_with_three_level_container_childs__return_childs_list_with_containers(self, uow):
        first_level_parent, first_level_childs = self._create_email_container_doc(uow)
        second_level_parent, second_level_childs = self._create_email_container_doc(uow, parent_doc=first_level_childs[0])
        third_level_parent, third_level_childs = self._create_email_container_doc(uow, parent_doc=second_level_childs[0])

        res_child_docs = uow.document.get_descendants(first_level_parent.pk, include_containers=True)

        assert sorted(res_child_docs, key=lambda x: x.pk) == sorted(
            chain(first_level_childs, second_level_childs, third_level_childs), key=lambda x: x.pk
        )
