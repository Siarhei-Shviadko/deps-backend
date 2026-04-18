import copy
import datetime
from functools import reduce

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import (
    DateTimeRangeObject,
    DocumentListFilterObject,
    PerPageOptions,
    SortingFieldsEnum,
)
from deps_documents.domain.entities.label import LabelEntity
from tests.factories import (
    DocumentEntityFactory,
    DocumentTypeEntityFactory,
    ReviewerFactory,
    TypedDocumentEntityFactory,
)


class TestCaseDocumentEntityRepositoryGetByFilter:
    document_entity = DocumentEntityFactory()
    total_entities = 20
    total_document_types = 3
    document_entities = [DocumentEntityFactory() for _ in range(total_entities)]
    typed_document_entities = [TypedDocumentEntityFactory() for _ in range(total_entities)]
    document_types = [DocumentTypeEntityFactory() for _ in range(total_document_types)]
    default_filtering = DocumentListFilterObject(
        page=1, per_page=total_entities, sort_field=SortingFieldsEnum.pk, sort_direct=True
    )

    def test_get_by_filter__without_arguments__return_all_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]

        result = uow.document.get_total_count_by_filter(filtering=self.default_filtering)

        assert result == len(documents)

    def test_get_by_filter__title__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]
        doc = documents[0]
        expected = [i.pk for i in documents if i.title == doc.title]
        filtering = copy.copy(self.default_filtering)
        filtering.title = doc.title

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__per_page_none__return_all_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]

        result = uow.document.get_list_by_filter(DocumentListFilterObject(per_page=PerPageOptions.FETCH_ALL_DOCS))

        assert len(result) == len(documents)

    def test_get_by_filter__states__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]
        doc = documents[0]
        doc1 = documents[1]
        expected = [i.pk for i in documents if i.state == doc.state or i.state == doc1.state]
        filtering = copy.copy(self.default_filtering)
        filtering.state = [doc.state, doc1.state]

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__reviewer__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]
        doc = documents[0]
        expected = [i.pk for i in documents if i.reviewer == doc.reviewer]
        filtering = copy.copy(self.default_filtering)
        filtering.reviewer = doc.reviewer

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__has_reviewer_false__return_documents(self, uow):
        uow.document.add(DocumentEntityFactory(reviewer=None))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        doc_with_reviewer = uow.document.add(DocumentEntityFactory(reviewer=reviewer))
        expected = set([doc_with_reviewer.pk])
        filtering = copy.copy(self.default_filtering)
        filtering.has_reviewer = True

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]
        assert set(result_pk) == expected

    def test_get_by_filter__has_reviewer_true__return_documents(self, uow):
        doc_no_reviewer = uow.document.add(DocumentEntityFactory(reviewer=None))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        uow.document.add(DocumentEntityFactory(reviewer=reviewer))
        expected = set([doc_no_reviewer.pk])
        filtering = copy.copy(self.default_filtering)
        filtering.has_reviewer = False

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]
        assert set(result_pk) == expected

    def test_get_by_filter__completed_state_and_no_reviewer__return_documents(self, uow):
        doc_no_reviewer1 = uow.document.add(DocumentEntityFactory(reviewer=None, state=DocumentStateEnum.COMPLETED))
        doc_no_reviewer2 = uow.document.add(DocumentEntityFactory(reviewer=None, state=DocumentStateEnum.COMPLETED))
        uow.document.add(DocumentEntityFactory(reviewer=None, state=DocumentStateEnum.IDENTIFICATION))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        uow.document.add(DocumentEntityFactory(reviewer=reviewer, state=DocumentStateEnum.COMPLETED))
        expected = set([doc_no_reviewer1.pk, doc_no_reviewer2.pk])
        filtering = copy.copy(self.default_filtering)
        filtering.has_reviewer = False
        filtering.state = [DocumentStateEnum.COMPLETED]

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]
        assert set(result_pk) == expected

    def test_get_by_filter__source__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in [DocumentEntityFactory(source_code="source_code") for _ in range(10)]]
        doc = documents[0]
        doc1 = documents[1]
        expected = [i.pk for i in documents if i.source_code == doc.source_code or i.source_code == doc1.source_code]
        filtering = copy.copy(self.default_filtering)
        filtering.source = [doc.source_code, doc1.source_code]

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__type__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.typed_document_entities]
        doc = documents[0]
        doc1 = documents[1]
        expected = [i.pk for i in documents if i.document_type == doc.document_type or i.document_type == doc1.document_type]
        filtering = copy.copy(self.default_filtering)
        filtering.document_type = [doc.document_type, doc1.document_type]

        result = uow.document.get_list_by_filter(filtering=filtering)
        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__except_type__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.typed_document_entities]
        doc = documents[0]
        doc1 = documents[1]
        expected = [i.pk for i in documents if i.document_type != doc.document_type and i.document_type != doc1.document_type]
        filtering = copy.copy(self.default_filtering)
        filtering.except_types = [doc.document_type, doc1.document_type]

        result = uow.document.get_list_by_filter(filtering=filtering)

        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__labels__return_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        document_with_label = uow.document.add(DocumentEntityFactory())
        label = uow.label.add(LabelEntity(name="label"))
        uow.document.add_label(label.pk, [document_with_label.pk])

        filtering = copy.copy(self.default_filtering)
        filtering.labels = [label.name]

        result = uow.document.get_list_by_filter(filtering=filtering)

        result_pk = [i.pk for i in result]

        assert set([document_with_label.pk]) == set(result_pk)

    def test_get_by_filter__date_range_greater_equal__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]
        datetime_test = datetime.datetime.now(tz=datetime.timezone.utc)
        expected = [i.pk for i in documents if i.date >= datetime_test]
        filtering = copy.copy(self.default_filtering)
        filtering.datetime_range = DateTimeRangeObject(datetime_test, None)

        result = uow.document.get_list_by_filter(filtering=filtering)

        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__date_range_less__return_documents(self, uow):
        documents = [uow.document.add(entity) for entity in self.document_entities]
        datetime_test = datetime.datetime.now(tz=datetime.timezone.utc)
        expected = [i.pk for i in documents if i.date < datetime_test]
        filtering = copy.copy(self.default_filtering)
        filtering.datetime_range = DateTimeRangeObject(None, datetime_test)

        result = uow.document.get_list_by_filter(filtering=filtering)

        result_pk = [i.pk for i in result]

        assert set(expected) == set(result_pk)

    def test_get_by_filter__sort_id__return_sort_id_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.pk

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: int(x.pk), result))

        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__sort_id__return_sort_id_asc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_direct = False
        filtering.sort_field = SortingFieldsEnum.pk

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: int(x.pk), result))

        assert self.is_sorted(res, reverse=False)

    @staticmethod
    def is_sorted(a, reverse=False):
        def straight_key(x):
            return x[0] <= x[1]

        def reverse_key(x):
            return x[0] >= x[1]

        if reverse:
            key = reverse_key
        else:
            key = straight_key

        return all(reduce(lambda acc, x: (*acc, True) if key(x) else (*acc, False), zip(a, a[1:] + a[-1:]), tuple()))

    def test_get_by_filter__sort_title__return_sort_title_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.title

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.title, result))
        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__sort_state__return_sort_state_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.state

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.state.value, result))
        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__sort_date__return_sort_date_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.date

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.date, result))
        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__sort_source__return_sort_source_desc_documents(self, uow):
        [uow.document.add(entity) for entity in [DocumentEntityFactory(source_code="source_code") for _ in range(10)]]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.source

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.source_code, result))
        assert self.is_sorted(res, reverse=True)

    @pytest.mark.skip
    def test_get_by_filter__sort_reviewer__return_sort_reviewer_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.reviewer

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.reviewer, result))
        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__sort_type__return_sort_type_desc_documents(self, uow):
        [uow.document.add(entity) for entity in self.typed_document_entities]
        [uow.document_type.save(document_type) for document_type in self.document_types]
        filtering = copy.copy(self.default_filtering)
        filtering.sort_field = SortingFieldsEnum.document_type

        result = uow.document.get_list_by_filter(filtering=filtering)

        res = tuple(map(lambda x: x.document_type, result))
        assert self.is_sorted(res, reverse=True)

    def test_get_by_filter__per_page__return_documents_per_page_amount(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.per_page = 5
        filtering.page = 1

        result = uow.document.get_list_by_filter(filtering=filtering)
        assert filtering.per_page == len(result)

    def test_get_by_filter__page__return_documents_start_from_page_amount(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.per_page = 3
        filtering.page = self.total_entities // filtering.per_page + 1

        result = uow.document.get_list_by_filter(filtering=filtering)

        assert self.total_entities - (filtering.page - 1) * filtering.per_page == len(result)

    def test_get_by_filter__ids__return(self, uow):
        [uow.document.add(entity) for entity in self.document_entities]
        filtering = copy.copy(self.default_filtering)
        filtering.ids = [x.pk for x in self.document_entities]

        result = uow.document.get_list_by_filter(filtering=filtering)

        assert len(result) == 0
