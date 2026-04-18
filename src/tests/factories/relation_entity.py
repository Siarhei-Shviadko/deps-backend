import random

import factory.fuzzy
from faker import Faker
from pytest_factoryboy import register

from deps_documents.domain.dtos import RelationDataObject
from deps_documents.domain.entities.relation import RelationEntity
from tests.factories.common import ListResponseMetaDataFactory

fake = Faker()


@register
class RelationEntityFactory(factory.Factory):
    class Meta:
        model = RelationEntity

    type = factory.Faker("text", max_nb_chars=16)
    code = factory.fuzzy.FuzzyText()
    metadata = factory.Dict({})
    assigned_documents = factory.LazyFunction(lambda: [fake.pyint() for _ in range(random.randint(2, 5))])
    parent_type = None
    parent_code = None


@register
class RelationListDataFactory(factory.Factory):
    class Meta:
        model = RelationDataObject

    meta = factory.SubFactory(ListResponseMetaDataFactory)
    content = factory.LazyAttribute(lambda self: [RelationEntityFactory() for _ in range(self.meta.size)])
