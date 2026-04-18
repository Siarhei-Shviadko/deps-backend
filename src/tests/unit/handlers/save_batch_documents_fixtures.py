import pytest
from deps_message_flow.commands.consumer import CommandMessage

from deps_documents.events_handler.command_handlers import SaveBatchDocuments
from deps_documents.events_handler.command_handlers.commands.save_batch_documents import (
    _FileData,
    _ProcessingParametersDict,
)


@pytest.fixture
def batch_id(faker):
    return faker.uuid4()


@pytest.fixture
def group_id(faker):
    return faker.uuid4()


@pytest.fixture
def metadata(faker):
    return {faker.name(): faker.text()}


@pytest.fixture
def processing_params(faker) -> _ProcessingParametersDict:
    return {
        "engine": faker.random_element(["gpt-4", "gpt-3.5-turbo", "davinci", "curie"]),
        "language": faker.language_code(),
        "llm_type": faker.random_element(["chat", "completion", "embedding"]),
        "parsing_features": None,
    }


@pytest.fixture
def file_data(faker, processing_params, metadata) -> _FileData:
    return {
        "id": faker.uuid4(),
        "name": faker.word(),
        "path": faker.file_path(extension=".pdf"),
        "document_type_id": str(faker.uuid4()),
        "processing_params": processing_params,
        "metadata": metadata,
    }


@pytest.fixture
def save_batch_documents_command_body(batch_id, group_id, tenant_id, file_data):
    return SaveBatchDocuments(batch_id=batch_id, group_id=group_id, files=[file_data])


@pytest.fixture
def document_id(faker) -> str:
    return str(faker.pyint())


@pytest.fixture
def save_batch_documents_command(mocker, save_batch_documents_command_body) -> CommandMessage[SaveBatchDocuments]:
    cm = mocker.Mock(CommandMessage)
    cm.command = save_batch_documents_command_body
    return cm
