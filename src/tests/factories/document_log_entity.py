import datetime

import factory
from faker import Faker
from pytest_factoryboy import register

from deps_documents.domain.constants import ActorEnum, DocumentLogEnum
from deps_documents.domain.entities import DocumentLogEntity

fake = Faker()


@register
class DocumentLogEntityFactory(factory.Factory):
    class Meta:
        model = DocumentLogEntity

    pk = None
    action = factory.Iterator(DocumentLogEnum)
    previous = factory.Faker("text", max_nb_chars=10)
    current = factory.Faker("text", max_nb_chars=10)
    created_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    document_id = factory.LazyFunction(lambda: str(fake.pyint()))
    actor = factory.Iterator(ActorEnum)
