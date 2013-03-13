from django.db import models
from django import forms

from tinymce.widgets import TinyMCE

from wheelcms_axle.content import type_registry, Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke
from wheelcms_axle.forms import formfactory


class News(Content):
    """ A news object """
    intro = models.TextField(blank=False)
    body = models.TextField(blank=False)

class NewsForm(formfactory(News)):
    body = forms.CharField(widget=TinyMCE(), required=False)

class NewsType(Spoke):
    model = News
    form = NewsForm

    title = "A simple News item"

    icon = "news.png"

template_registry.register(NewsType, "wheelcms_spokes/news_view.html", "Basic News view", default=True)
type_registry.register(NewsType)
