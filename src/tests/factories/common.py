import factory
from faker import Faker
from pytest_factoryboy import register

from deps_documents.domain.dtos import ListResponseMetaDataObject

fake = Faker()


@register
class ListResponseMetaDataFactory(factory.Factory):
    class Meta:
        model = ListResponseMetaDataObject

    total = fake.pyint(min_value=1, max_value=10)
    size = fake.pyint(min_value=1, max_value=total)
