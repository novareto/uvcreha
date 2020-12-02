import pytest
from roughrider.workflow import WorkflowItem, Transition, Action
from docmanager.models import Document
from docmanager.workflow import DocumentWorkflow, document_workflow, notify_trigger


def test_workflow_default():

    doc = Document(
        az='az',
        username='user',
        body='My document',
        content_type='base_doc',
    )

    wrapper = document_workflow(doc, request=object())

    assert wrapper.get_state() == DocumentWorkflow.states.inquiry
    assert wrapper.get_possible_transitions() == (
        Transition(
            action=Action(
                'Send',
                triggers=[notify_trigger]
            ),
            origin=DocumentWorkflow.states.inquiry,
            target=DocumentWorkflow.states.sent
        ),
    )

    wrapper.set_state(DocumentWorkflow.states.sent)
    assert doc.state == DocumentWorkflow.states.sent.name
    assert wrapper.get_state() == DocumentWorkflow.states.sent


def test_workflow_error():

    doc = Document(
        az='az',
        username='user',
        body='My document',
        content_type='base_doc',
    )

    wrapper = document_workflow(doc, request=object())
    assert wrapper.get_state() == DocumentWorkflow.states.inquiry

    with pytest.raises(LookupError) as exc:
        wrapper.set_state(DocumentWorkflow.states.approved)

    assert str(exc.value) == "No transition from states.inquiry to states.approved"
