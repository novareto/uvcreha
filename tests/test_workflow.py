import pytest
from roughrider.workflow import WorkflowItem, Transition, Action
from docmanager.models import Document
from docmanager.workflow import DocumentWorkflow, document_workflow, notify_trigger


def test_workflow_default():

    doc = Document(
        az='az',
        uid='user',
        body='My document',
        content_type='base_doc',
    )

    wrapper = document_workflow(doc, request=object())

    assert wrapper.state == DocumentWorkflow.states.inquiry
    assert wrapper.get_possible_transitions() == (
        Transition(
            action=Action('Send'),
            origin=DocumentWorkflow.states.inquiry,
            target=DocumentWorkflow.states.sent
        ),
    )

    wrapper.transition_to(DocumentWorkflow.states.sent)
    assert doc.state == DocumentWorkflow.states.sent.name
    assert wrapper.state == DocumentWorkflow.states.sent


def test_workflow_error():

    doc = Document(
        az='az',
        uid='user',
        body='My document',
        content_type='base_doc',
    )

    wrapper = document_workflow(doc, request=object())
    assert wrapper.state == DocumentWorkflow.states.inquiry

    with pytest.raises(LookupError) as exc:
        wrapper.transition_to(DocumentWorkflow.states.approved)

    assert str(exc.value) == "No transition from states.inquiry to states.approved"
