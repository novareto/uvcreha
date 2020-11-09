import reg
from typing import Callable
from heapq import heappush


class NamedComponents:

    __slots__ = ('_components',)

    def __init__(self):
        self._components = {}

    def register(self, component, name):
        self._components.__setitem__(name, component)

    def get(self, name):
        return self._components.get(name)

    def __getitem__(self, name):
        return self._components.__getitem__(name)

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

    def unregister(self, name):
        del self._components[name]


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
