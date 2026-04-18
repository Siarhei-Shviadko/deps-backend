from tests.factories import DocumentEntityFactory


def test_document_entity_creation__needs_parsing_and_parsing_features():
    created_document = DocumentEntityFactory(
        needs_parsing=True,
        parsing_features={"feature1", "feature2"},
    )

    assert created_document.needs_parsing is True


def test_document_entity_creation__no_parsing_features():
    created_document = DocumentEntityFactory(
        needs_parsing=True,
        parsing_features=None,
    )

    assert created_document.needs_parsing is False


def test_document_entity_creation__no_needs_parsing__but_with_features():
    created_document = DocumentEntityFactory(
        needs_parsing=False,
        parsing_features={"feature1", "feature2"},
    )

    assert created_document.needs_parsing is False


def test_document_entity_creation__needs_parsing_is_none__but_with_features():
    created_document = DocumentEntityFactory(
        parsing_features={"feature1", "feature2"},
    )

    assert created_document.needs_parsing is True


def test_document_entity_creation__needs_parsing_is_none__no_features():
    created_document = DocumentEntityFactory(
        parsing_features={},
    )

    assert created_document.needs_parsing is False
