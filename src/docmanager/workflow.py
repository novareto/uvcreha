from roughrider.workflow.workflow import Workflow, State
from docmanager.models import Document


#submitted = State(
#    title="Submitted",
#    identifier="myproject.submitted",
#    destinations={
#        'Publish': 'myproject.published'
#    }
#)
#
#
#published =  State(
#    title="Published",
#    identifier="myproject.published",
#    destinations={
#        'Re-submit': 'myproject.submitted'
#    }
#)


#class DocumentWorkflow(Workflow):
#    pass
#
#
#DocumentWorkflow.register(Document, submitted, default=True)
#DocumentWorkflow.register(Document, published)
