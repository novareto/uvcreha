import reg
from pkg_resources import iter_entry_points


class ModelsRegistry(dict):
    __slots__ = ()

    def register(self, name, model):
        if name in self:
            raise KeyError(f'Model {name} already exists.')
        self[name] = model

    def load(self):
        self.clear()
        for loader in iter_entry_points('docmanager.models'):
            logger.info(f'Register model "{loader.name}"')
            self.register(loader.name, loader.load())


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


class PluginsRegistry:

    __slots__ = ('_plugins',)

    def __init__(self):
        self._plugins = {}

    def register(self, name, plugin):
        self._plugins.__setitem__(name, plugin)

    def get(self, name):
        return self._plugins.get(name)

    def __len__(self):
        return len(self._plugins)

    def __iter__(self):
        return iter(self._plugins)


class MiddlewaresRegistry:

    __slots__ = ('_middlewares',)

    def __init__(self):
        self._middlewares = []

    def register(self, middleware, order=0):
        self._middlewares.append((order, middleware))

    def __len__(self):
        return len(self._middlewares)

    def __iter__(self):
        def ordered(e):
            return -e[0], repr(e[1])
        yield from (m[1] for m in sorted(self._middlewares, key=ordered))
