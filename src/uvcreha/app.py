import reiter.view.utils
from reiter.events.meta import Subscribers
from reiter.application.browser import registries
from roughrider.routing.route import NamedRoutes


browser = NamedRoutes(extractor=reiter.view.utils.routables)
api = NamedRoutes(extractor=reiter.view.utils.routables)
ui = registries.UIRegistry()
events = Subscribers()
