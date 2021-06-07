from roughrider import workflow


class ModelWorkflowItem(workflow.WorkflowItem):
    @property
    def state(self):
        return self.workflow.get(self.item.get("state"))

    @state.setter
    def state(self, wfstate):
        self.item["state"] = wfstate.name


def ValidUser(item, **namespace):
    if not item["email"]:
        raise workflow.Error(message=f"User {item} needs a valid email.")


class UserWorkflow(workflow.Workflow):

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


class DocumentWorkflow(workflow.Workflow):

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


class FileWorkflow(workflow.Workflow):

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


@document_workflow.subscribe("Send")
@document_workflow.subscribe("Approve")
def notify_trigger(transition, item, request, **ns):
    print(f"This is a notification: {item}, {request}.")
