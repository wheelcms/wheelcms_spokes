from django.db import models
from django import forms

from django.utils.html import strip_tags
from django.utils.text import Truncator

from wheelcms_axle.content import type_registry
from wheelcms_axle.content import Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke, indexfactory, SpokeCharField
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
        if self.instance.node.children().exists():
            return "folder_page.png"
        return "page.png"

    def index_description(self):
        """ truncate body text if no explicit description available """
        if self.instance.description:
            return self.instance.description

        return Truncator(strip_tags(self.instance.body)).words(50,
                         truncate=" ...")

    @classmethod
    def index(cls):
        class PageIndex(indexfactory(cls)):
            description = SpokeCharField(spoke=cls,
                                         stored=True, indexed=False,
                                         model_attr="index_description")

        return PageIndex

type_registry.register(PageType)
template_registry.register(PageType, "wheelcms_spokes/page_view.html",
                           "Basic Page view", default=True)
