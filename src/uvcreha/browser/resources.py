# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2020 NovaReto GmbH
# # cklinger@novareto.de


from fanstatic import Library, Resource, Group


library = Library("uvcreha", "static")

custom_css = Resource(library, "siguvtheme.css")

sidebar_css = Resource(library, "sidebar.css")

main_css = Resource(library, "main.css")

main_js = Resource(library, "main.js")

application_webpush = Resource(library, "webpush.js")

webpush_subscription = Resource(
    library, "webpush_subscription.js", depends=[application_webpush]
)

bootstrap_css = Resource(
    library,
    "uvc_serviceportal_bootstrap.css",
    compiler="sass",
    source="scss/siguv.scss",
)



f_input_css = Resource(library, 'fileinput/fileinput.min.css')  
f_input_js  = Resource(library, 'fileinput/fileinput.min.js')
f_input_jsf = Resource(library, 'fileinput/piexif.min.js')
f_input_de = Resource(library, 'fileinput/de.js')

f_input_group = Group([f_input_css, f_input_js, f_input_jsf, f_input_de])


bootstrap_js = Resource(library, "bootstrap.bundle.js", depends=[main_js], bottom=True)

siguvtheme = Group(
    [
        application_webpush,
        custom_css,
        main_css,
        sidebar_css,
        bootstrap_css,
        bootstrap_js,
        f_input_group
    ]
)
