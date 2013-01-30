from django.db import models
from wheelcms_axle.models import type_registry
from wheelcms_spokes.templates import template_registry
from wheelcms_axle.models import FileContent
from wheelcms_spokes.models import FileSpoke

class File(FileContent):
    """ Holds a file """
    ## cannot be named file - that's used for the content base relation
    storage = models.FileField(upload_to="files", blank=False)

class FileType(FileSpoke):
    model = File

    title = "A file"
    children = ()

template_registry.register(FileType, "wheelcms_spokes/file_view.html", "Basic News view", default=True)
type_registry.register(FileType)
