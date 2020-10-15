# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2020 NovaReto GmbH
# # cklinger@novareto.de


from fanstatic import Library, Resource, Group


library = Library('adhoc', 'static')
custom_css = Resource(library, 'siguvtheme.css')

sidebar_css = Resource(library, 'sidebar.css')
main_css = Resource(library, 'main.css')
main_js = Resource(library, 'main.js')
bootstrap_css = Resource(library, 'uvc_serviceportal_bootstrap.css', compiler="sass", source="scss/siguv.scss")
bootstrap_js = Resource(library, 'bootstrap.bundle.js', depends=[main_js,], bottom=True)
siguvtheme = Group([custom_css, main_css, sidebar_css, bootstrap_css, bootstrap_js])
