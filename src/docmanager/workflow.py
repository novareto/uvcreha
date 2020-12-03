from roughrider import workflow


class ModelWorkflowItem(workflow.WorkflowItem):

    def get_state(self):
        return self.workflow.get(self.item.state)

    def set_state(self, state):
        if (error := self.check_reachable(state)):
            raise error
        self.item.state = state.name


def notify_trigger(item, request, **ns):
    print(f'This is a notification: {item}, {request}.')


class ValidUser(workflow.Validator):

    @classmethod
    def validate(cls, item, **namespace):
        if not item.email:
            raise Error(message=f'User {item} needs a valid email.')


class UserWorkflow(workflow.Workflow):

    class states(workflow.WorkflowState):
        pending = 'Pending'
        active = 'Active'
        inactive = 'Inactive'
        closed = 'Closed'

    transitions = workflow.Transitions((
        workflow.Transition(
            origin=states.pending,
            target=states.active,
            action=workflow.Action(
                'Activate',
                constraints=[ValidUser],
            )
        ),
        workflow.Transition(
            origin=states.active,
            target=states.inactive,
            action=workflow.Action('De-activate')
        ),
        workflow.Transition(
            origin=states.inactive,
            target=states.active,
            action=workflow.Action('Re-activate')
        ),
        workflow.Transition(
            origin=states.inactive,
            target=states.closed,
            action=workflow.Action('Close')
        ),
    ))

    wrapper = ModelWorkflowItem


class DocumentWorkflow(workflow.Workflow):

    class states(workflow.WorkflowState):
        inquiry = 'Inquiry'
        sent = 'Sent'
        approved = 'Approved'

    transitions = workflow.Transitions((
        workflow.Transition(
            origin=states.inquiry,
            target=states.sent,
            action=workflow.Action(
                'Send',
                triggers=[notify_trigger]
            )
        ),
        workflow.Transition(
            origin=states.sent,
            target=states.approved,
            action=workflow.Action(
                'Approve',
                triggers=[notify_trigger]
            )
        )
    ))

    wrapper = ModelWorkflowItem


document_workflow = DocumentWorkflow('inquiry')
user_workflow = UserWorkflow('pending')
