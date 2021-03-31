from uvcreha.messaging import message_center
from uvcreha.app import browser, api


#@browser.subscribe('document_created')
#@api.subscribe('document_created')
def document_messaging(request, uid, document):
    message = 'my doc message'
    return message_center(request, uid, document, message)


#@browser.subscribe('folder_created')
#@api.subscribe('folder_created')
def folder_messaging(request, uid, folder):
    message = 'my folder message'
    return message_center(request, uid, folder, message)
