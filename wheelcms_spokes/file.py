import mimetypes

from django.db import models
from django.http import HttpResponse

from wheelcms_axle.models import type_registry
from wheelcms_spokes.templates import template_registry
from wheelcms_axle.models import FileContent
from wheelcms_spokes.models import FileSpoke

class File(FileContent):
    """ Holds a file """
    ## cannot be named file - that's used for the content base relation
    content_type = models.CharField(blank=True, max_length=256)
    filename = models.CharField(blank=True, max_length=256)
    storage = models.FileField(upload_to="files", blank=False)

    def save(self, *a, **b):
        """
            Intercept save, fill in defaults for filename and mimetype if not
            explicitly set
        """
        if not self.filename:
            self.filename = self.storage.name or self.title
            ## guess extension if missing?
        if not self.content_type:
            type, encoding = mimetypes.guess_type(self.filename)
            if type is None:
                type = "application/octet-stream"
            self.content_type = type
        return super(File, self).save(*a, **b)

## hide filename from form - extract it from uploaded file.
##
## provide list of mimetypes for mimetype, provide detection option

class FileType(FileSpoke):
    model = File

    title = "A file"
    children = ()

    def detail_template(self):
        """ A small detail template, used in browse modal """
        return "wheelcms_spokes/file_detail.html"

    def handle_download(self):
        """ provide a direct download

            What's the best option: redirect to {{MEDIA_URL}}/<path> or
            serve from the cms? The former is far more efficient (can be handled
            by the application server), the latter allows more restrictions,
            headers, mangling, etc.

            For now, let's choose the inefficient option
        """
        ## test workflow state / permissions! XXX

        filename = self.instance.filename or self.instance.title
        content_type = self.instance.content_type or "application/octet-stream"

        response = HttpResponse(self.instance.storage, content_type=content_type)
        response['Content-Type'] = content_type

        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

template_registry.register(FileType, "wheelcms_spokes/file_view.html", "Basic News view", default=True)
type_registry.register(FileType)
