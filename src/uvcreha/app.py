import reiter.view.meta
from roughrider.events.registry import Subscribers
from reiter.application.browser import registries
from roughrider.routing.route import NamedRoutes


browser = NamedRoutes(extractor=reiter.view.meta.routables)
api = NamedRoutes(extractor=reiter.view.meta.routables)
ui = registries.UIRegistry()
events = Subscribers()
