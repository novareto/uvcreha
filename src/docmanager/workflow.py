from roughrider import workflow


def notify_trigger(item, request, **ns):
    print(f'This is a notification: {item}, {request}.')


class DocumentWorkflow(workflow.Workflow):

    class wrapper(workflow.WorkflowItem):

        def get_state(self):
            return self.workflow.get(self.item.state)

        def set_state(self, state):
            if (error := self.check_reachable(state)):
                raise error
            self.item.state = state.name

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


document_workflow = DocumentWorkflow('inquiry')
