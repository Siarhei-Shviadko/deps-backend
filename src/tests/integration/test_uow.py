import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory


@pytest.fixture
def uow_factory(units_of_work):
    return units_of_work.uow


class TestUnitOfWork:
    @staticmethod
    def add_document(uow):
        return uow.document.add(DocumentEntityFactory())

    def test_uow__operation_succeed__database_updated(self, uow_factory, domain_services):
        with uow_factory() as uow:
            document = self.add_document(uow)
            uow.commit()
        assert domain_services.document().get(document.pk) == document

    def test_uow__operation_fails__database_not_updated(self, uow_factory, domain_services):
        with uow_factory() as uow:
            document = self.add_document(uow)
        with pytest.raises(DocumentNotFoundError):
            domain_services.document().get(document.pk)

    def test_uow__nested_operation_succeeds__database_updated(self, uow_factory, domain_services):
        with uow_factory() as _uow:
            document = self.add_document(_uow)
            with uow_factory() as _second_uow:
                _ = _second_uow.document.get(document.pk)
                with uow_factory() as _third_uow:
                    _third_uow.document.delete(document)
                    with uow_factory() as _fourth_uow:
                        document2 = self.add_document(_fourth_uow)
                        _fourth_uow.commit()
                    # check that doc2 saved already
                    _third_uow.document.get(document2.pk)
                    _third_uow.commit()
                # check that document already deleted
                with pytest.raises(DocumentNotFoundError):
                    _second_uow.document.get(document.pk)
                    assert False
                _second_uow.commit()
            _uow.commit()
        with pytest.raises(DocumentNotFoundError):
            domain_services.document().get(document.pk)
        assert domain_services.document().get(document2.pk) == document2

    def test_uow__nested_operation_fails__database_not_updated(self, uow_factory, domain_services):
        with pytest.raises(DocumentNotFoundError):
            with uow_factory() as _uow:
                document = self.add_document(_uow)
                with uow_factory() as _second_uow:
                    document1 = self.add_document(_second_uow)
                    with uow_factory() as _third_uow:
                        document2 = self.add_document(_third_uow)
                        with uow_factory() as _fourth_uow:
                            raise DocumentNotFoundError
                        _third_uow.commit()
                    _second_uow.commit()
                _uow.commit()

        for docpk in (document2.pk, document1.pk, document.pk):
            with pytest.raises(DocumentNotFoundError):
                domain_services.document().get(docpk)

    def test_uow__nested_operation__sql_exception__database__not_updated(self, uow_factory, domain_services):
        with pytest.raises(DocumentNotFoundError):
            with uow_factory() as _uow:
                document = self.add_document(_uow)
                with uow_factory() as _second_uow:
                    _second_uow.document.delete(document)
                    with uow_factory() as _third_uow:
                        _third_uow.document.get(document.pk)
                        _third_uow.commit()
                    _second_uow.commit()
                _uow.commit()

        with pytest.raises(DocumentNotFoundError):
            domain_services.document().get(document.pk)

    def test_uow__outer_operation_fails_after_inner_commit__database__not_updated(self, uow_factory, domain_services):
        with pytest.raises(DocumentNotFoundError):
            with uow_factory() as _uow:
                document1 = self.add_document(_uow)
                with uow_factory() as _second_uow:
                    document2 = self.add_document(_second_uow)
                    with uow_factory() as _third_uow:
                        document3 = self.add_document(_third_uow)
                        _third_uow.commit()
                    _second_uow.commit()
                raise DocumentNotFoundError

        for doc in (document1, document2, document3):
            with pytest.raises(DocumentNotFoundError):
                domain_services.document().get(doc.pk)

    def test_uow__outer_operation_not_commits_after_inner_commit__database__not_updated(self, uow_factory, domain_services):
        # Should not be the case. Made for illustration. Expected for code to raise exception in case of errors.
        with uow_factory() as _uow:
            document1 = self.add_document(_uow)
            with uow_factory() as _second_uow:
                document2 = self.add_document(_second_uow)
                with uow_factory() as _third_uow:
                    document3 = self.add_document(_third_uow)
                    _third_uow.commit()
                _second_uow.commit()

        for doc in (document1, document2, document3):
            with pytest.raises(DocumentNotFoundError):
                domain_services.document().get(doc.pk)
