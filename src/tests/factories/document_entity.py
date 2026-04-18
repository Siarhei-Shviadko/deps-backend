import datetime
import random
from typing import Any
from uuid import uuid4

import factory
from faker import Faker
from pytest_factoryboy import register

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import DocumentFilesDataObject, DocumentListDataObject
from deps_documents.domain.entities import (
    BlobFile,
    CommentEntity,
    CommunicationEntity,
    DocumentEntity,
    DocumentMetadata,
    DocumentTypeEntity,
    ErrorEntity,
    GroupEntity,
    LabelEntity,
    ParsingFeature,
    PreprocessResultEntity,
    Reviewer,
    ScrapedMetadataEntity,
)
from deps_documents.domain.entities.document import ContainerEmailMetadata
from tests.factories.common import ListResponseMetaDataFactory

fake = Faker()
document_type_code_list = ["BelarusPassport", "DirectionalSurvey", "CompletionReport"]
entity_type_list = ["email", "generic", "image", "custom"]
language_list = ["eng", "rus", "chi_sim", "deu", "spa", "ukr"]


@register
class ReviewerFactory(factory.Factory):
    class Meta:
        model = Reviewer

    id = factory.Faker("uuid4")
    email = factory.Faker("ascii_email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


@register
class GroupEntityFactory(factory.Factory):
    class Meta:
        model = GroupEntity

    id = factory.Faker("uuid4")
    name = factory.Faker("domain_word")


@register
class BlobFileFactory(factory.Factory):
    class Meta:
        model = BlobFile

    blob_name = factory.Faker("file_path", extension="jpg", depth=5)


@register
class PreprocessResultEntityFactory(factory.Factory):
    class Meta:
        model = PreprocessResultEntity

    entity_type = factory.Iterator(entity_type_list)
    preview: list[Any] = []
    processing = factory.LazyFunction(lambda: [BlobFileFactory() for i in range(random.randint(1, 3))])
    meta = None


@register
class ScrapedMetadataEntityFactory(factory.Factory):
    class Meta:
        model = ScrapedMetadataEntity

    api_number = factory.LazyFunction(lambda: "{}-{}".format(fake.pyint(), fake.pyint()))


@register
class CommentEntityFactory(factory.Factory):
    class Meta:
        model = CommentEntity

    text = factory.Faker("text", max_nb_chars=100)
    created_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    created_by = factory.Faker("uuid4")


@register
class CommunicationEntityFactory(factory.Factory):
    class Meta:
        model = CommunicationEntity

    comments = factory.LazyFunction(lambda: [CommentEntityFactory() for _ in range(random.randint(0, 3))])


@register
class ErrorEntityFactory(factory.Factory):
    class Meta:
        model = ErrorEntity

    description = factory.Faker("sentence", nb_words=10)
    in_state = factory.Iterator(DocumentStateEnum)


@register
class ContainerEmailMetadataFactory(factory.Factory):
    class Meta:
        model = ContainerEmailMetadata

    first_level_child_count = None

    subject = factory.Faker("domain_word")
    sender = factory.Faker("email")
    recipients = factory.LazyFunction(lambda: [fake.email()])
    cc = factory.LazyFunction(lambda: [fake.email()])
    body = factory.Faker("sentence")
    date = factory.LazyFunction(lambda: str(fake.date_time(datetime.timezone.utc)))


DocumentTestStates = list(DocumentStateEnum)
DocumentTestStates.remove(DocumentStateEnum.VALIDATION)


@register
class DocumentEntityFactory(factory.Factory):
    class Meta:
        model = DocumentEntity

    pk = None
    parent_id = None

    title = factory.Faker("file_name")
    state = factory.Iterator(DocumentTestStates)
    files = factory.LazyFunction(lambda: list([BlobFileFactory() for i in range(random.randint(1, 3))]))
    document_type = factory.Faker("name")
    sub_type = factory.Faker("name")
    date = factory.LazyFunction(lambda: fake.date_time(datetime.timezone.utc))
    source_code = None
    reviewer = None
    language = factory.Iterator(language_list)
    engine = "TESSERACT"
    llm_type = factory.Faker("random_element", elements=(None, "gpt4"))
    parsing_features = factory.Faker(
        "random_element", elements=(None, {ParsingFeature.IMAGES, ParsingFeature.TABLES, ParsingFeature.TEXT})
    )

    scraped_metadata = factory.SubFactory(ScrapedMetadataEntityFactory)
    communication = factory.SubFactory(CommunicationEntityFactory)
    preview_documents = factory.LazyFunction(lambda: list([BlobFileFactory() for i in range(random.randint(0, 3))]))
    processing_documents = factory.LazyFunction(lambda: list([BlobFileFactory() for i in range(random.randint(0, 3))]))
    error = factory.SubFactory(ErrorEntityFactory)
    container_type = None
    container_metadata = None
    group = None
    needs_unification = True
    needs_extraction = True
    needs_parsing = None
    needs_validation = None
    needs_output_exporting = None
    needs_review = None


@register
class TypedDocumentEntityFactory(DocumentEntityFactory):
    document_type = factory.Iterator(document_type_code_list)


@register
class DocumentListDataFactory(factory.Factory):
    class Meta:
        model = DocumentListDataObject

    meta = factory.SubFactory(ListResponseMetaDataFactory)
    content = factory.LazyAttribute(lambda self: [DocumentEntityFactory() for _ in range(self.meta.size)])


@register
class DocumentFilesDataFactory(factory.Factory):
    class Meta:
        model = DocumentFilesDataObject

    document_name = "Fake_file"
    files_names = ["path1/fake_file_name_1.jpg"]


@register
class LabelEntityFactory(factory.Factory):
    class Meta:
        model = LabelEntity

    pk = None
    name = factory.Faker("name")


class DocumentMetadataFactory(factory.Factory):
    class Meta:
        model = DocumentMetadata

    document_id = factory.Sequence(lambda n: n)
    metadata = {"parameter": "data"}


@register
class DocumentTypeEntityFactory(factory.Factory):
    class Meta:
        model = DocumentTypeEntity

    id = factory.Iterator(document_type_code_list)
    tenant = factory.Faker("uuid4")
    name = factory.Iterator(document_type_code_list)
