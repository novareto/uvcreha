import reg
from typing import Callable
from heapq import heappush
from pkg_resources import iter_entry_points


class NamedComponents:

    __slots__ = ('_components',)

    def __init__(self):
        self._components = {}

    def register(self, component, name):
        self._components.__setitem__(name, component)

    def get(self, name):
        return self._components.get(name)

    def __len__(self):
        return len(self._components)

    def __iter__(self):
        return iter(self._components)

    def component(self, name):
        """Component decorator
        """
        def register_component(component):
            self.register(component, name)
            return component
        return register_component


class PriorityList:

    __slots__ = ('_components',)

    def __init__(self):
        self._components = []

    def register(self, item: Callable, priority: int):
        heappush(self._components, (priority, item))

    def __len__(self):
        return len(self._components)

    def __iter__(self):
        return iter(self._components)

    def __reversed__(self):
        return reversed(self._components)


class ModelsRegistry:

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key('content_type'))
    def document_model(self, request, content_type="default"):
        raise RuntimeError("Unknown document type.")

    def document(self, request):
        def add_document_model(model):
            def dispatcher(request, content_type):
                return model

            schema = model.schema()
            content_type = schema['properties']['content_type']['const']
            return self.document_model.register(
                reg.methodify(dispatcher),
                request=request, content_type=content_type)
        return add_document_model

    @reg.dispatch_method(reg.match_instance('request'))
    def file_model(self, request):
        raise RuntimeError("Unknown file type.")

    def file(self, request):
        def add_file_model(model):
            def dispatcher(request):
                return model

            return self.file_model.register(
                reg.methodify(dispatcher), request=request)
        return add_file_model

    @reg.dispatch_method(reg.match_instance('request'))
    def user_model(self, request):
        raise RuntimeError("Unknown user type.")

    def user(self, request):
        def add_user_model(model):
            def dispatcher(request):
                return model

            return self.user_model.register(
                reg.methodify(dispatcher), request=request)
        return add_user_model


class UIRegistry:

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key('name'))
    def layout(self, request, name):
        raise RuntimeError("Unknown layout.")

    def register_layout(self, request, name='default'):
        def add_layout(layout):
            return self.layout.register(
                reg.methodify(layout), request=request, name=name)
        return add_layout

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key("name"))
    def slot(self, request, name):
        raise RuntimeError("Unknown slot.")

    def register_slot(self, request, name):
        def add_slot(slot):
            return self.slot.register(
                reg.methodify(slot), request=request, name=name)
        return add_slot
