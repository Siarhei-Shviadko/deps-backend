from typing import Any, Dict, List, Optional
from uuid import uuid4

from deps_message_flow.events.common import DomainEvent
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_documents.constants import DOCUMENTS_EXCHANGER
from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.entities import DocumentEntity
from deps_documents.domain.events.commands import (
    ClassifyDocument,
    ExtractData,
    PreprocessDocument,
)
from deps_documents.domain.events.events import DocumentCreated
from deps_documents.domain.interfaces import IPipelineManagerService


class ChoreographyManager(IPipelineManagerService):
    def __init__(self, publisher: DomainEventPublisher):
        self._publisher = publisher

        self.pipeline_step_map = {
            PipelineStepsEnum.PREPROCESS: self.preprocess,
            PipelineStepsEnum.IDENTIFICATION: self.classification,
            PipelineStepsEnum.EXTRACTION: self.extraction,
        }

    def preprocess(
        self,
        document: DocumentEntity,
        extraction_params: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
        extract_data: bool = False,
    ) -> List[DomainEvent]:
        return [
            PreprocessDocument(
                document_id=document.pk,
                files=[file.blob_name for file in document.files],
                identify_document=document.document_type is not None,
                extract_data=extract_data,
                extract_attachments=document.extract_attachments,
                document_type=document.document_type,
                engine=engine if engine else None,
                language=language,
            ),
        ]

    def classification(
        self,
        document: DocumentEntity,
        extraction_params: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
        extract_data: bool = False,
    ) -> List[DomainEvent]:
        return [ClassifyDocument(document_id=document.pk, engine=engine, language=language, extraction_params=extraction_params)]

    def extraction(
        self,
        document: DocumentEntity,
        extraction_params: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
        extract_data: bool = False,
    ) -> List[DomainEvent]:
        return [ExtractData(document_id=document.pk, language=language, engine=engine)]

    def run(
        self,
        document: DocumentEntity,
        identify_document: bool,
        extract_data: bool,
        extraction_params: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        events = [
            DocumentCreated(
                document_id=document.pk,
                files=[file.blob_name for file in document.files],
                identify_document=identify_document,
                extract_data=extract_data,
                extract_attachments=document.extract_attachments,
                extraction_params=extraction_params,
                document_type=document.document_type,
                engine=engine if engine else None,
                language=language,
            ),
        ]
        self._publisher.publish(
            DOCUMENTS_EXCHANGER,
            str(document.pk),
            events,
            headers={"ID": uuid4().hex},
        )

    def run_step(
        self,
        document: DocumentEntity,
        step: PipelineStepsEnum,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        self._publisher.publish(
            DOCUMENTS_EXCHANGER,
            str(document.pk),
            self.pipeline_step_map[step](
                document=document,
                engine=engine,
                language=language,
                model_blob_path=model_blob_path,
            ),
            headers={"ID": uuid4().hex},
        )

    def run_from_step(
        self,
        document: DocumentEntity,
        step: PipelineStepsEnum,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        model_blob_path: Optional[str] = None,
    ) -> None:
        self._publisher.publish(
            DOCUMENTS_EXCHANGER,
            str(document.pk),
            self.pipeline_step_map[step](
                document=document,
                engine=engine,
                language=language,
                model_blob_path=model_blob_path,
                extract_data=True,
            ),
            headers={"ID": uuid4().hex},
        )
