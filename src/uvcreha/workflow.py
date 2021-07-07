from roughrider import workflow
from uvcreha.events import WorkflowTransitionEvent
from reiter.events import Subscribers


class ModelWorkflowItem(workflow.WorkflowItem):

    @property
    def state(self):
        return self.workflow.get(self.item.get("state"))

    @state.setter
    def state(self, wfstate):
        self.item["state"] = wfstate.name

    def apply_transition(self, transition: workflow.Transition):
        super().apply_transition(transition)
        self.workflow.notify(WorkflowTransitionEvent(
            transition, self.item, **self.namespace
        ))


def ValidUser(item, **namespace):
    if not item["email"]:
        raise workflow.Error(message=f"User {item} needs a valid email.")


class Workflow(workflow.Workflow):

    def __init__(self, default_state):
        super().__init__(default_state)
        self.subscribers: Subscribers = Subscribers()

    def notify(self, *args, **kwargs):
        return self.subscribers.notify(*args, **kwargs)

    def subscribe(self, event_type):
        return self.subscribers.subscribe(event_type)


class UserWorkflow(Workflow):

    wrapper = ModelWorkflowItem

    class states(workflow.WorkflowState):
        pending = "in Prüfung"
        active = "Aktiv"
        inactive = "Inaktiv"
        closed = "Geschlossen"

    transitions = workflow.Transitions(
        (
            workflow.Transition(
                origin=states.pending,
                target=states.active,
                action=workflow.Action(
                    "Activate",
                    constraints=[ValidUser],
                ),
            ),
            workflow.Transition(
                origin=states.active,
                target=states.inactive,
                action=workflow.Action("De-activate"),
            ),
            workflow.Transition(
                origin=states.inactive,
                target=states.active,
                action=workflow.Action("Re-activate"),
            ),
            workflow.Transition(
                origin=states.inactive,
                target=states.closed,
                action=workflow.Action("Close"),
            ),
        )
    )


class DocumentWorkflow(Workflow):

    wrapper = ModelWorkflowItem

    class states(workflow.WorkflowState):
        inquiry = "Anfrage"
        sent = "Gesendet"
        approved = "Bestätigt/Abgeschlossen"

    transitions = workflow.Transitions(
        (
            workflow.Transition(
                origin=states.inquiry,
                target=states.sent,
                action=workflow.Action("Send"),
            ),
            workflow.Transition(
                origin=states.sent,
                target=states.approved,
                action=workflow.Action("Approve"),
            ),
        )
    )


class FileWorkflow(Workflow):

    wrapper = ModelWorkflowItem

    class states(workflow.WorkflowState):
        created = "Created"
        validated = "Validated"
        closed = "Closed"

    transitions = workflow.Transitions(
        (
            workflow.Transition(
                origin=states.created,
                target=states.validated,
                action=workflow.Action("Validate"),
            ),
            workflow.Transition(
                origin=states.validated,
                target=states.closed,
                action=workflow.Action("Close"),
            ),
        )
    )


document_workflow = DocumentWorkflow("inquiry")
user_workflow = UserWorkflow("pending")
file_workflow = FileWorkflow("created")
