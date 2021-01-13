import logging
import importscan
import pkg_resources


def load(logger=None):
    for plugin in pkg_resources.iter_entry_points('docmanager.plugins'):
        module = plugin.load()
        importscan.scan(module)
        log = logger is not None and logger.info or logging.info
        log(f"Plugin '{plugin.name}' loaded.")
