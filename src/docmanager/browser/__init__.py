import logging
import chameleon.zpt.loader
from pkg_resources import iter_entry_points


logger = logging.getLogger()


def tales_expressions():
    """Tales registry
    """
    expressions = {}
    for ept in iter_entry_points(group="chameleon.tales"):
        if ept.name in expressions:
            continue
            raise KeyError(
                "TALES name %r is defined more than once" % ept.name)
        expressions[ept.name] = ept.load()
        logger.debug(
            "Register Chameleon Expression Extension %s" % ept.name)
    return expressions


class TemplateLoader(chameleon.zpt.loader.TemplateLoader):

    def __init__(self, *args, **kwargs):
        self.tales = tales_expressions()
        super().__init__(*args, **kwargs)

    def load(self, filename, format=None):
        template = super().load(filename, format=format)
        template.expression_types.update(self.tales)
        return template

    __getitem__ = load
