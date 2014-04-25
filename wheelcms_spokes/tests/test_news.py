"""
    type specific test based on spoke base tests
"""
from wheelcms_axle.tests.test_spoke import BaseSpokeTest, BaseSpokeTemplateTest
from wheelcms_spokes.news import NewsType, News
from wheelcms_axle.tests.test_impexp import BaseSpokeImportExportTest
from wheelcms_axle.tests.test_search import BaseTestSearch
from wheelcms_axle.tests.utils import MockedQueryDict

class TestNewsSpokeTemplate(BaseSpokeTemplateTest):
    """ Test the News type """
    type = NewsType

    def valid_data(self, **kw):
        """ return additional data for News validation """
        return MockedQueryDict(intro="Hi There!", body="Hello World", **kw)

class TestNewsSpoke(BaseSpokeTest):
    """ Test the News type """
    type = NewsType

class TestNewsSpokeImpExp(BaseSpokeImportExportTest):
    type = NewsType
    spoke = NewsType

class TestNewsSpokeSearch(BaseTestSearch):
    type = NewsType
