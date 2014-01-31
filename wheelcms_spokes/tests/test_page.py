"""
    type specific test based on spoke base tests
"""
from wheelcms_axle.tests.test_spoke import BaseSpokeTest, BaseSpokeTemplateTest
from wheelcms_spokes.page import PageType, Page
from wheelcms_axle.tests.test_impexp import BaseSpokeImportExportTest
from wheelcms_axle.tests.test_search import BaseTestSearch
from wheelcms_axle.tests.utils import MockedQueryDict

class TestPageSpokeTemplate(BaseSpokeTemplateTest):
    """ Test the Page type """
    type = PageType

    def valid_data(self, **kw):
        """ return additional data for Page validation """
        return MockedQueryDict(body="Hello World", **kw)


class TestPageSpoke(BaseSpokeTest):
    """ Test the Page type """
    type = PageType

class TestPageSpokeImpExp(BaseSpokeImportExportTest):
    type = Page
    spoke = PageType

class TestPageSpokeSearch(BaseTestSearch):
    type = PageType
