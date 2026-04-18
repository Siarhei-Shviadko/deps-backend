def test_document_assigned_relations(relation_with_docs, document_service):
    for doc_id in relation_with_docs.assigned_documents:
        doc = document_service.get(doc_id)
        assert relation_with_docs.code == doc.assigned_relations[0].code
        assert relation_with_docs.type == doc.assigned_relations[0].type
