from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.engine import RowProxy

from deps_documents.domain.constants import (
    ContainerTypesEnum,
    DocumentAssignmentStatusEnum,
    DocumentPriorityEnum,
    DocumentStateEnum,
)
from deps_documents.domain.entities import (
    BlobFile,
    BlobFileMetadata,
    CommunicationEntity,
    ContainerEmailMetadata,
    DocumentEntity,
    DocumentMetadata,
    ErrorEntity,
    GroupEntity,
    LabelEntity,
    ParsingFeature,
    RelationEntity,
    Reviewer,
    ScrapedMetadataEntity,
)
from deps_documents.infrastructure.repositories.helpers import (
    cast_from_db_pk,
    cast_to_db_pk,
)


def build_document_entity(  # noqa: WPS210
    doc_in_db: Union[RowProxy, dict],
    labels: List[LabelEntity],
    communication: CommunicationEntity,
    assigned_relations: List[RelationEntity] = None,
    reviewer: Optional[Reviewer] = None,
    group: Optional[GroupEntity] = None,
) -> DocumentEntity:
    scraped_metadata_entity = ScrapedMetadataEntity(api_number=doc_in_db["scraped_api_number"])
    preview_documents = convert_dicts_to_blob_files(doc_in_db["preview_documents"])
    processing_documents = convert_dicts_to_blob_files(doc_in_db["processing_documents"])

    error = ErrorEntity(
        description=doc_in_db["error_description"],
        in_state=doc_in_db["error_in_state"] and DocumentStateEnum(doc_in_db["error_in_state"]),
    )

    container_type = ContainerTypesEnum(doc_in_db["container_type"]) if doc_in_db["container_type"] is not None else None
    first_level_child_count = (
        doc_in_db["first_level_child_count"]
        if hasattr(  # noqa: WPS421
            doc_in_db,
            "first_level_child_count",
        )
        else None
    )
    container_metadata = convert_container_metadata(container_type, first_level_child_count, doc_in_db["container_metadata"])
    assigned_relations = assigned_relations if assigned_relations is not None else []
    assignment_status = DocumentAssignmentStatusEnum(doc_in_db["assignment_status"]) if doc_in_db["assignment_status"] else None
    priority = DocumentPriorityEnum(doc_in_db["priority"]) if doc_in_db["priority"] else None

    if (
        parsing_features := doc_in_db["processing_parameters"].get("parsing_features")
        if doc_in_db["processing_parameters"]
        else None
    ):
        parsing_features = {ParsingFeature(feature) for feature in parsing_features}

    return DocumentEntity(
        pk=cast_from_db_pk(doc_in_db["id"]),
        parent_id=cast_from_db_pk(doc_in_db["parent_id"]) if doc_in_db["parent_id"] else None,
        scraped_metadata=scraped_metadata_entity if bool(doc_in_db["scraped_api_number"]) else None,
        communication=communication,
        preview_documents=preview_documents,
        processing_documents=processing_documents,
        error=error if doc_in_db["error_description"] is not None else None,
        container_type=container_type,
        container_metadata=container_metadata,
        title=doc_in_db["title"],
        state=DocumentStateEnum(doc_in_db["state"]),
        files=convert_dicts_to_blob_files(doc_in_db["files"]),
        document_type=doc_in_db["document_type"],
        sub_type=doc_in_db["sub_type"],
        source_code=doc_in_db["source_code"],
        reviewer=reviewer,
        date=doc_in_db["date"],
        language=doc_in_db["language"],
        engine=doc_in_db["engine"],
        llm_type=doc_in_db["llm_type"],
        labels=labels,
        assigned_relations=assigned_relations,
        assignment_status=assignment_status,
        priority=priority,
        group=group,
        parsing_features=parsing_features,
        needs_unification=doc_in_db["processing_parameters"].get("needs_unification")
        if doc_in_db["processing_parameters"]
        else True,
        needs_extraction=doc_in_db["processing_parameters"].get("needs_extraction")
        if doc_in_db["processing_parameters"]
        else True,
        needs_parsing=doc_in_db["processing_parameters"].get("needs_parsing") if doc_in_db["processing_parameters"] else False,
        needs_review=doc_in_db["processing_parameters"].get("needs_review") if doc_in_db["processing_parameters"] else None,
        needs_validation=doc_in_db["processing_parameters"].get("needs_validation")
        if doc_in_db["processing_parameters"]
        else None,
        needs_output_exporting=doc_in_db["processing_parameters"].get("needs_output_exporting")
        if doc_in_db["processing_parameters"]
        else None,
    )


def convert_dict_to_document_main_info(doc_in_db: Union[RowProxy, dict]) -> dict:
    return {
        "pk": cast_from_db_pk(doc_in_db["id"]),
        "type": doc_in_db["document_type"],
        "title": doc_in_db["title"],
        "engine": doc_in_db["engine"],
        "language": doc_in_db["language"],
        "llm_type": doc_in_db["llm_type"],
        "files": convert_dicts_to_blob_files(doc_in_db["files"]),
        "state": DocumentStateEnum(doc_in_db["state"]),
        "error_in_state": DocumentStateEnum(doc_in_db["error_in_state"]) if doc_in_db["error_in_state"] else None,
        "metadata": doc_in_db["metadata"],
    }


def build_dict_from_entity(doc_entity: DocumentEntity) -> Dict[str, Any]:
    metadata_files = convert_blob_files_to_dicts(doc_entity.files)
    preview_documents = convert_blob_files_to_dicts(doc_entity.preview_documents)
    processing_documents = convert_blob_files_to_dicts(doc_entity.processing_documents)

    container_metadata = None
    if doc_entity.container_metadata:
        container_metadata_dict = asdict(doc_entity.container_metadata)
        if "first_level_child_count" in container_metadata_dict:
            container_metadata_dict.pop("first_level_child_count")
        container_metadata = container_metadata_dict

    document = {
        "parent_id": cast_to_db_pk(doc_entity.parent_id) if doc_entity.parent_id else None,
        "title": doc_entity.title,
        "state": doc_entity.state,
        "files": metadata_files,
        "document_type": doc_entity.document_type,
        "sub_type": doc_entity.sub_type,
        "date": doc_entity.date,
        "source_code": doc_entity.source_code if doc_entity.source_code else None,
        "reviewer": doc_entity.reviewer.id if doc_entity.reviewer else None,
        "language": doc_entity.language,
        "engine": doc_entity.engine,
        "llm_type": doc_entity.llm_type,
        "scraped_api_number": doc_entity.scraped_metadata and doc_entity.scraped_metadata.api_number,
        "preview_documents": preview_documents,
        "processing_documents": processing_documents,
        "error_description": doc_entity.error and doc_entity.error.description,
        "error_in_state": doc_entity.error and ((doc_entity.error.in_state.value or None) if doc_entity.error.in_state else None),
        "container_type": doc_entity.container_type,
        "container_metadata": container_metadata,
        "assignment_status": doc_entity.assignment_status,
        "priority": doc_entity.priority,
        "group_id": doc_entity.group.id if doc_entity.group is not None else None,
        "processing_parameters": {
            "needs_unification": doc_entity.needs_unification,
            "needs_extraction": doc_entity.needs_extraction,
            "needs_parsing": doc_entity.needs_parsing,
            "parsing_features": [feature.value for feature in doc_entity.parsing_features]
            if doc_entity.parsing_features
            else None,
            "needs_review": doc_entity.needs_review,
            "needs_validation": doc_entity.needs_validation,
            "needs_output_exporting": doc_entity.needs_output_exporting,
        },
    }
    if doc_entity.pk:
        document["id"] = cast_to_db_pk(doc_entity.pk)
    return document


def convert_blob_files_to_dicts(blob_files: List[BlobFile]) -> List[Dict[str, Any]]:
    blob_dicts = []
    for blob_file in blob_files:
        blob_dict: Dict[str, Any] = {"blobName": blob_file.blob_name}
        if blob_file.metadata:
            blob_dict["metadata"] = {"width": blob_file.metadata.width, "height": blob_file.metadata.height}
        blob_dicts.append(blob_dict)

    return blob_dicts


def convert_dicts_to_blob_files(blob_file_dicts: List[Dict[str, Any]]) -> List[BlobFile]:
    if blob_file_dicts is None:
        return []

    blob_files = []
    for blob_file_dict in blob_file_dicts:
        metadata = blob_file_dict.get("metadata")
        if metadata:
            metadata = BlobFileMetadata(width=metadata["width"], height=metadata["height"])
        blob_files.append(BlobFile(blob_name=blob_file_dict.get("blobName"), metadata=metadata))

    return blob_files


def convert_container_metadata(container_type: ContainerTypesEnum, first_level_child_count: int, container_metadata):
    if container_type == ContainerTypesEnum.EMAIL:
        return ContainerEmailMetadata(first_level_child_count=first_level_child_count, **container_metadata)
    return None


def build_document_metadata_from_db(document_metadata_db: Union[RowProxy, dict]) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=cast_from_db_pk(document_metadata_db["document_id"]),
        metadata=document_metadata_db["metadata"],
    )


def build_dict_from_document_metadata_entity(document_metadata: DocumentMetadata) -> dict[str, Any]:
    return {
        "document_id": cast_to_db_pk(document_metadata.document_id),
        "metadata": document_metadata.metadata,
    }


def build_reviewer_entity(reviewer: RowProxy) -> Reviewer:
    return Reviewer(
        id=reviewer["id"],
        email=reviewer["email"],
        first_name=reviewer["first_name"],
        last_name=reviewer["last_name"],
    )


def build_dict_from_reviewer_entity(reviewer: Reviewer) -> Dict[str, Any]:
    return {
        "id": reviewer.id,
        "email": reviewer.email,
        "first_name": reviewer.first_name,
        "last_name": reviewer.last_name,
    }
