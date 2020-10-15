from pathlib import Path

from autoroutes import Routes
import horseman.meta
import horseman.response
import roughrider.routing.node

from adhoc.layout import template_endpoint
from adhoc.request import Request
from adhoc.models import User


class Application(horseman.meta.SentryNode,
                  roughrider.routing.node.RoutingNode):

    __slots__ = ('config', )
    request_factory = Request

    def __init__(self):
        self.routes = Routes()

    def set_configuration(self, config: dict):
        self.config = config


application = Application()
