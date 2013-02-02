import re
import mimetypes

from django.http import HttpResponse
from django import forms
from wheelcms_axle.models import Content, Node
from wheelcms_axle.workflows.default import DefaultWorkflow

from wheelcms_axle.models import type_registry
from wheelcms_spokes.templates import template_registry

from two.ol.util import classproperty

class BaseForm(forms.ModelForm):
    class Meta:
        exclude = ["node", "meta_type", "owner", "classes"]

    slug = forms.Field(required=False)

    def __init__(self, parent, attach=False, *args, **kwargs):
        """
            Django will put the extra slug field at the bottom, below
            all model fields. I want it just after the title field
        """
        super(BaseForm, self).__init__(*args, **kwargs)
        slug = self.fields.pop('slug')
        titlepos = self.fields.keyOrder.index('title')
        self.fields.insert(titlepos+1, 'slug', slug)
        self.parent = parent
        self.attach = attach
        if attach:
            self.fields.pop('slug')

        templates = template_registry.get(self._meta.model, [])
        if templates:
            self.fields['template'] = forms.ChoiceField(choices=templates,
                                                        required=False)
        else:
            self.fields.pop('template')  ## will default to content_view

        self.fields['state'] = forms.ChoiceField(choices=self.workflow_choices(),
                                                 initial=self.workflow_default(),
                                                 required=False)
        if self.instance and self.instance.node and self.instance.node.isroot():
            self.fields.pop("slug")

    def workflow_choices(self):
        """
            return valid choices. Is actually context dependend (not all states
            can be reached from a given state)
        """
        spoke = type_registry.get(self._meta.model.get_name())
        return spoke.workflowclass.states

    def workflow_default(self):
        """
            Return default state for active workflow
        """
        spoke = type_registry.get(self._meta.model.get_name())
        return spoke.workflowclass.default

    def clean_slug(self):
        if self.attach:
            return

        slug = self.data.get('slug', '').strip().lower()

        parent_path = self.parent.path

        if not slug:
            slug = re.sub("[^%s]+" % Node.ALLOWED_CHARS, "-",
                          self.cleaned_data.get('title', '').lower()
                          )[:Node.MAX_PATHLEN].strip("-")
            try:
                existing = Node.objects.filter(path=parent_path
                                               + "/" + slug).get()
                base_slug = slug[:Node.MAX_PATHLEN-6] ## some space for counter
                count = 1
                while existing and existing != self.instance.node:
                    slug = base_slug + str(count)
                    existing = Node.objects.filter(path=self.parent.path
                                                   + "/" + slug).get()
                    count += 1

            except Node.DoesNotExist:
                pass

        if not Node.validpathre.match(slug):
            raise forms.ValidationError("Only numbers, letters, _-")
        try:
            existing = Node.objects.filter(path=parent_path + "/" + slug
                                          ).get()
            if existing != self.instance.node:
                raise forms.ValidationError("Name in use")
        except Node.DoesNotExist:
            pass

        return slug

    def clean_template(self):
        template = self.data.get('template')
        if not template:
            return ""

        if not template_registry.valid_for_model(self._meta.model, template):
            raise forms.ValidationError("Invalid template")
        return template


def formfactory(type):
    class Form(BaseForm):
        class Meta(BaseForm.Meta):
            model = type
            exclude = BaseForm.Meta.exclude + ["created", "modified"]
    return Form

def FileFormfactory(type, light=False):
    """
        Provide a form that has an optional title field. If left
        unspecified, take the filename from the uploaded file in stead.
    """
    base = formfactory(type)

    class Form(base):
        class Meta(base.Meta):
            if light:
                fields = [ 'title', 'state', 'storage' ]

        content_type = forms.ChoiceField(
                        choices=(('', 'detect type'),) +
                                 tuple((x, x) for x in
                                       sorted(mimetypes.types_map.values())
                                ), required=False)


        def __init__(self, *args, **kw):
            """ make the title field not required """
            super(Form, self).__init__(*args, **kw)
            self.fields['title'].required = False
            if light:
                self.fields['slug'].widget = forms.HiddenInput()
                self.fields['template'].widget = forms.HiddenInput()

        def clean_title(self):
            """ generate title based on filename if necessary """
            title = self.data.get('title', '').strip()
            try:
              if not title:
                  title = self.files.get('storage').name
            except AttributeError:
                ## there is no file upload. This will cause validation
                ## to fail at a later stage but it shouldn't produce
                ## errors now
                title = ''
            return title
    return Form


class Spoke(object):
    model = Content  ## is it smart to set this to Content? A nonsensible default..
    workflowclass = DefaultWorkflow

    ## None means no restrictions, () means no subcontent allowed
    children = None

    ## can it be implicitly added?
    implicit_add = True

    ## explicit children - explicit children that can be added
    explicit_children = None

    def __init__(self, o):
        self.o = o
        self.instance = o  ## keep self.o for backward compat

    @classproperty
    def form(cls):
        return formfactory(cls.model)

    @classproperty
    def light_form(cls):
        """ a smaller, lightweight form with minimal requirements """
        return cls.form

    @classmethod
    def name(cls):
        """ This needs namespacing. But a model determines its name based
            on the classname and doesn't know about namespaces or packages """
        return cls.model.get_name()  ## app_label

    @classmethod
    def title(cls):
        """ a default title """
        return cls.model._meta.object_name + " content"

    def workflow(self):
        return self.workflowclass(self)

    def view_template(self):
        if not self.o.template or \
           not template_registry.valid_for_model(self.model, self.o.template):
            default = template_registry.defaults.get(self.model)
            if default:
                return default

            all = template_registry.get(self.model, [])
            if len(all) == 1:
                return all[0][0]

            return "wheelcms_axle/content_view.html"

        return self.o.template

    def detail_template(self):
        """ A small detail template, used in browse modal """
        return "wheelcms_axle/popup_detail.html"

    def fields(self):
        """ iterate over fields in model """
        for i in self.o._meta.fields:
            yield (i.name, getattr(self.o, i.name))

    @classmethod
    def addable_children(cls):
        """ return spokes that can be added as children """
        def addable(t):
            """ check it it's addable, implicitly or explicitly """
            if t.implicit_add:
                return True
            explicit = set(cls.children or ()) | set(cls.explicit_children or ())
            return t in explicit

        if cls.children is None:
            ch = [t for t in type_registry.values() if addable(t)]
        else:
            ch = cls.children

        return ch


class FileSpoke(Spoke):
    @classproperty
    def form(cls):
        return FileFormfactory(cls.model)

    @classproperty
    def light_form(cls):
        return FileFormfactory(cls.model, light=True)

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


import wheelcms_spokes.page
import wheelcms_spokes.news
import wheelcms_spokes.image
import wheelcms_spokes.file

