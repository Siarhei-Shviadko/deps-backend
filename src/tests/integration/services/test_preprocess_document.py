from deps_documents.domain.constants import DocumentStateEnum, UseCaseResponseStatusEnum
from tests.factories import DocumentEntityFactory, PreprocessResultEntityFactory
from tests.utils import ContainerDocumentCreatorMixin


class TestAcceptPreprocessResultUseCase(ContainerDocumentCreatorMixin):
    def test_execute__document_exists__returns_document_pk(self, app, uow):
        document = uow.document.add(DocumentEntityFactory(pk="1", state=DocumentStateEnum.PREPROCESSING))

        use_case = app.use_cases.service_preprocess_document()
        use_case_response = use_case.execute(use_case.Request(document_id=document.pk, preprocess_entities=[]))

        assert use_case_response.value.document_entity.pk == "1"

    def test_execute__email__returns_state_success(self, app, uow):
        parent_document = self._create_email_container_doc(uow, child_docs_number=1)[0]
        use_case = app.use_cases.service_preprocess_document()
        use_case_response = use_case.execute(
            use_case.Request(
                document_id=parent_document.pk, preprocess_entities=[PreprocessResultEntityFactory(entity_type="email")]
            )
        )
        assert use_case_response.status == UseCaseResponseStatusEnum.SUCCESS

    def test_execute__document_does_not_exist__returns_resource_error(self, app):
        use_case = app.use_cases.service_preprocess_document()

        use_case_response = use_case.execute(use_case.Request(document_id="1337", preprocess_entities=[]))

        assert use_case_response.status == UseCaseResponseStatusEnum.ERROR
