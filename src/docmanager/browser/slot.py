import ast
from abc import ABC, abstractmethod
from chameleon.codegen import template
from chameleon.astutil import Symbol


class Slot(ABC):

    def __init__(self, context, request, view, name: str):
        self.context = context
        self.request = request
        self.view = view
        self.name = name

    def update(self):
        pass

    @abstractmethod
    def __call__(self, request) -> str:
        """Returns HTML
        """


def query_slot(econtext, name):
    """Compute the result of a slot expression
    """
    request = econtext.get('request')
    return request.app.ui.slot(request, name)


class SlotExpr(object):
    """
    This is the interpreter of a slot: expression
    """
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, target, engine):
        slot_name = self.expression.strip()
        value = template(
            "query_slot(econtext, name)",
            query_slot=Symbol(query_slot),  # ast of query_slot
            name=ast.Str(s=slot_name),  # our name parameter to query_slot
            mode="eval")
        return [ast.Assign(targets=[target], value=value)]
