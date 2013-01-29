"""
    Test spoke related code / forms / behaviour
"""

from wheelcms_axle.models import Node, TypeRegistry, type_registry
from wheelcms_spokes.templates import TemplateRegistry
import wheelcms_spokes.templates
from wheelcms_axle.tests.models import Type1Type

DEFAULT = "wheelcms_axle/content_view.html"

class BaseSpokeTest(object):
    """
        Basic spoke testing
    """
    type = None
    typename = None

    def setup(self):
        """ override the global registry """
        self.registry = TypeRegistry()
        type_registry.set(self.registry)
        self.registry.register(self.type)

    def test_name(self, client):
        """
            Name generation
        """
        model = self.type.model()
        model.save()
        spoke = self.type(model)

        assert spoke.name() == self.typename

    def test_fields(self, client):
        """
            Test the fields() method that iterates over the
            model instances fields
        """
        model = self.type.model()
        model.save()
        spoke = self.type(model)
        fields = dict(spoke.fields())

        assert 'title' in fields

        return fields  ## for additional tests


class BaseSpokeTemplateTest(object):
    """
        Test template related validation/behaviour
    """
    def valid_data(self):
        """ return formdata required for validation to succeed """
        return {}

    def valid_files(self):
        """ return formdata files required for validation to succeed """
        return {}

    def setup(self):
        """ create clean local registries, make sure it's used globally """
        self.reg = TemplateRegistry()
        wheelcms_spokes.templates.template_registry.set(self.reg)

        self.registry = TypeRegistry()
        type_registry.set(self.registry)
        self.registry.register(self.type)
        self.root = Node.root()

    def test_empty(self, client):
        """ An empty registry """
        form = self.type.form(parent=self.root)
        assert 'template' not in form.fields
        model = self.type.model()
        model.save()
        assert self.type(model).view_template() == DEFAULT

    def test_single(self, client):
        """ An single template registered """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        form = self.type.form(parent=self.root)
        assert 'template' in form.fields
        assert form.fields['template'].choices == [('foo/bar', 'foo bar')]
        model = self.type.model()
        model.save()
        assert self.type(model).view_template() == 'foo/bar'

    def test_default(self, client):
        """ If there's a default, it should be used """
        model = self.type.model()
        model.save()
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        self.reg.register(self.type, "foo/bar2", "foo bar", default=True)
        self.reg.register(self.type, "foo/bar3", "foo bar", default=False)
        assert self.type(model).view_template() == "foo/bar2"

    def test_explicit(self, client):
        """ unless there's an explicit other selection """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        self.reg.register(self.type, "foo/bar2", "foo bar", default=True)
        self.reg.register(self.type, "foo/bar3", "foo bar", default=False)
        model = self.type.model(template="foo/bar3")
        model.save()
        assert self.type(model).view_template() == "foo/bar3"

    def test_form_validation_fail(self, client):
        """ Only registered templates are allowed """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        form = self.type.form(parent=self.root, data={'template':"bar/foo"})
        assert not form.is_valid()
        assert 'template' in form.errors

    def test_form_validation_success(self, client):
        """ In the end it should succeed """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        self.reg.register(self.type, "foo/bar2", "foo bar", default=True)
        self.reg.register(self.type, "foo/bar3", "foo bar", default=False)
        p = Node.root()
        data = self.valid_data()
        data['slug'] = 's'
        data['title'] = 't'
        data['template'] = 'foo/bar3'

        form = self.type.form(parent=p, data=data, files=self.valid_files())

        assert form.is_valid()
        assert form.cleaned_data['template'] == "foo/bar3"

    def test_slug_exists(self, client):
        """ a slug has been chosen that's already in use """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        p = Node.root()
        p.add('foo')
        data = self.valid_data()
        data['slug'] = 'foo'
        data['title'] = 't'
        data['template'] = 'foo/bar'

        form = self.type.form(parent=p, data=data, files=self.valid_files())

        assert not form.is_valid()
        assert 'slug' in form.errors
        assert form.errors['slug'].pop() == 'Name in use'  ## fragile

    def test_slug_generate(self, client):
        """ test slug generation """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        p = Node.root()
        data = self.valid_data()
        data['title'] = 'Hello World'
        data['template'] = 'foo/bar'

        form = self.type.form(parent=p, data=data, files=self.valid_files())

        assert form.is_valid()

    def test_slug_generate_complex(self, client):
        """ test slug generation """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        p = Node.root()
        data = self.valid_data()
        data['title'] = 'Hello World, What\'s up?'
        data['slug'] = ''
        data['template'] = 'foo/bar'

        form = self.type.form(parent=p, data=data, files=self.valid_files())

        assert form.is_valid()
        assert form.cleaned_data['slug'] == 'hello-world-what-s-up'

    def test_slug_generate_conflict(self, client):
        """ slug generation should not create duplicate slugs """
        self.reg.register(self.type, "foo/bar", "foo bar", default=False)
        p = Node.root()
        p.add('foo')
        data = self.valid_data()
        data['slug'] = ''
        data['title'] = 'foo'
        data['template'] = 'foo/bar'

        form = self.type.form(parent=p, data=data, files=self.valid_files())

        assert form.is_valid()
        assert form.cleaned_data['slug'] == 'foo1'

class TestType1Spoke(BaseSpokeTest):
    """
        Run base tests on test type 'type1'
    """
    type = Type1Type
    typename = "type1"

    def test_fields(self, client):
        """ base tests + extra field """
        fields = super(TestType1Spoke, self).test_fields(client)
        assert 't1field' in fields


class TestType1SpokeTemplate(BaseSpokeTemplateTest):
    """
        Run base template tests on test type 'type1'
    """
    type = Type1Type
    typename = "type1"

from wheelcms_spokes.models import Spoke

class ModellessSpoke(Spoke):
    """
        Handle the absence of a model
    """
    @classmethod
    def name(cls):
        return cls.__name__.lower()

class TestImplicitAddition(object):
    """
        Test implicit/explicit addition of children
    """
    def setup(self):
        """ local registry, install it globally """
        self.registry = TypeRegistry()
        type_registry.set(self.registry)

    def test_explicit(self, client):
        """ Simple case, no restrictions """
        class T1(ModellessSpoke):
            implicit_add = True  ## default

        class T2(ModellessSpoke):
            children = None

        self.registry.register(T1)
        self.registry.register(T2)

        assert T1 in T2.addable_children()

    def test_non_implicit(self, client):
        """ T1 cannot be added explicitly """
        class T1(ModellessSpoke):
            implicit_add = False

        class T2(ModellessSpoke):
            children = None

        self.registry.register(T1)
        self.registry.register(T2)

        assert T1 not in T2.addable_children()

    def test_non_implicit_but_children(self, client):
        """ T1 cannot be added explicitly but is in T2's children """
        class T1(ModellessSpoke):
            implicit_add = False

        class T2(ModellessSpoke):
            children = (T1, )

        self.registry.register(T1)
        self.registry.register(T2)

        assert T1 in T2.addable_children()

    def test_non_implicit_but_exp_children(self, client):
        """ T1 cannot be added explicitly but is in T2's explicit
            children """
        class T1(ModellessSpoke):
            implicit_add = False

        class T2(ModellessSpoke):
            explicit_children = (T1, )

        self.registry.register(T1)
        self.registry.register(T2)

        assert T1 in T2.addable_children()
