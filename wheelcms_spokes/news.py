from django.db import models
from wheelcms_axle.content import type_registry, Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke

class News(Content):
    """ A news object """
    intro = models.TextField(blank=False)
    body = models.TextField(blank=False)


class NewsType(Spoke):
    model = News

    title = "A simple News item"


template_registry.register(NewsType, "wheelcms_spokes/news_view.html", "Basic News view", default=True)
type_registry.register(NewsType)
