from django.db import models
from wheelcms_axle.models import type_registry
from wheelcms_spokes.templates import template_registry
from wheelcms_axle.models import ImageContent
from wheelcms_spokes.models import FileSpoke


class Image(ImageContent):
    """ Holds an image.  """
    ## cannot be named image - that's used for the content base relation
    storage = models.ImageField(upload_to="images", blank=False)

class ImageType(FileSpoke):
    model = Image

    title = "An image"
    children = ()

    def detail_template(self):
        """ A small detail template, used in browse modal """
        return "wheelcms_spokes/image_detail.html"

template_registry.register(ImageType, "wheelcms_spokes/image_view.html", "Basic Image view", default=True)
type_registry.register(ImageType)
