from uvcreha.app import browser
from reiter.view.meta import View
from uvcreha.browser.layout import TEMPLATES
from uvcreha import contenttypes


@browser.register("/users/{uid}/files/{az}", name="file.view")
class FileIndex(View):
    template = TEMPLATES["file_view.pt"]

    def GET(self):
        file_ct = contenttypes.registry["file"]
        doc_ct = contenttypes.registry["document"]
        file = file_ct.bind(self.request.database).find_one(**self.params)
        docs = doc_ct.bind(self.request.database).find(
            uid=file.data["uid"], az=file.data["az"]
        )
        return dict(documents=docs, request=self.request, context=file)
