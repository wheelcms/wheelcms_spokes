"""
    type specific test based on spoke base tests
"""
from wheelcms_axle.tests.test_spoke import BaseSpokeTest, BaseSpokeTemplateTest
from wheelcms_spokes.news import NewsType, News
from wheelcms_axle.tests.test_impexp import BaseSpokeImportExportTest


class TestNewsSpokeTemplate(BaseSpokeTemplateTest):
    """ Test the News type """
    type = NewsType
    typename = "news"

    def valid_data(self):
        """ return additional data for News validation """
        return dict(intro="Hi There!", body="Hello World")

class TestNewsSpoke(BaseSpokeTest):
    """ Test the News type """
    type = NewsType
    typename = "news"

class TestNewsSpokeImpExp(BaseSpokeImportExportTest):
    type = News
    spoke = NewsType
