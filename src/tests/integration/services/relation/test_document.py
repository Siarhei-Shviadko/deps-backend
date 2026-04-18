def test_get_document__pass(relation_service, relation_created_docs_assigned):
    relation = relation_created_docs_assigned
    documents = relation_service.get_document(relation)
    assert documents.meta.size == len(relation.assigned_documents)
    assert documents.meta.total == len(relation.assigned_documents)

    for doc in documents.content:
        assert int(doc.pk) in relation.assigned_documents
