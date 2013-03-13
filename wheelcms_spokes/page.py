from django.db import models
from django import forms

from wheelcms_axle.content import type_registry
from wheelcms_axle.content import Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke
from wheelcms_axle.forms import formfactory

from tinymce.widgets import TinyMCE
from tinymce.models import HTMLField

##
## Either HTMLField or TinyMCE widget. But a demonstration on how to alter
## a Spoke's form is also nice to have.

class Page(Content):
    """ A simple page object """
    body = models.TextField(blank=False)
    # body = HTMLField(blank=False)

class PageForm(formfactory(Page)):
    body = forms.CharField(widget=TinyMCE(), required=False)


class PageType(Spoke):
    document_fields = Spoke.document_fields + ("body", )

    model = Page
    title = "A simple HTML page"
    form = PageForm

    @property
    def icon(self):
        if self.instance.node.children():
            return "folder_page.png"
        return "page.png"


type_registry.register(PageType)
template_registry.register(PageType, "wheelcms_spokes/page_view.html",
                           "Basic Page view", default=True)
