from deps_documents.api.models.document.document import DocumentModel
from deps_documents.domain.entities import DocumentEntity


def dump_document_for_request(document_entity: DocumentEntity):
    result = DocumentModel.from_domain(document_entity).model_dump(by_alias=True)
    if "files" in result:
        for file in result["files"]:
            del file["url"]
    if "previewDocuments" in result:
        for page in result["previewDocuments"]:
            del result["previewDocuments"][page]["url"]
    if "processingDocuments" in result:
        for page in result["processingDocuments"]:
            del result["processingDocuments"][page]["url"]
    if "groupId" in result:
        del result["groupId"]
    if "groupInfo" in result:
        del result["groupInfo"]
    return result
