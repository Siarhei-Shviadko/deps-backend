def check_document_response_fields(document_json):
    expected_fields = [
        "_id",
        "communication",
        "containerMetadata",
        "containerType",
        "date",
        "documentType",
        "modelName",
        "engine",
        "error",
        "files",
        "labels",
        "language",
        "llmType",
        "parentId",
        "previewDocuments",
        "processingDocuments",
        "reviewer",
        "source",
        "state",
        "title",
        "assignedRelations",
        "assignmentStatus",
        "priority",
        "groupId",
        "groupInfo",
    ]

    response_fields = document_json.keys()
    assert sorted(expected_fields) == sorted(
        response_fields
    ), f"Extra: {set(response_fields) - set(expected_fields)}, Missing: {set(expected_fields) - set(response_fields)}"
