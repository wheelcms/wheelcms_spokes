"""
    test file/image based on spoke base tests
"""

import pytest

from wheelcms_axle.tests.test_spoke import BaseSpokeTemplateTest, \
                                             BaseSpokeTest
from wheelcms_spokes.file import FileType, File
from wheelcms_spokes.image import ImageType, Image
from django.core.files.uploadedfile import SimpleUploadedFile
from wheelcms_axle.tests.test_impexp import BaseSpokeImportExportTest


class BaseImageFileTemplateTest(BaseSpokeTemplateTest):
    """
        Shared customization/tests
    """
    def valid_files(self):
        """ return an image, will work for both file and image uploads """
        return dict(storage=SimpleUploadedFile("foo.png", 
                    'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                    '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'))

    def test_children_restriction(self, client):
        """ by default, a file or image can't have kids """
        assert self.type.children is not None
        assert len(self.type.children) == 0

class BaseImageFileTest(BaseSpokeTest):
    def test_download(self, client):
        data = 'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00' \
                   '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        storage=SimpleUploadedFile("foo.png", data)
        f = self.type.model(storage=storage,
                            filename="bar.png",
                            content_type="application/octet-stream").save()
        spoke = self.type(f)
        response = spoke.download(None, None, 'download')
        assert response.content == data
        assert response.has_header('Content-Disposition')
        assert response['Content-Disposition'] == \
               'attachment; filename=bar.png'
        assert response['Content-Type'] == "application/octet-stream"

    def test_download_defaults(self, client):
        data = 'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00' \
                   '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        storage=SimpleUploadedFile("foo.png", data)
        f = self.type.model(storage=storage).save()
        spoke = self.type(f)
        response = spoke.download(None, None, 'download')
        assert response.content == data
        assert response.has_header('Content-Disposition')
        assert response['Content-Disposition'] == \
               'attachment; filename=foo.png'
        assert response['Content-Type'] == "image/png"

    def test_filename_slash(self, client):
        """ make sure the filename cannot contain directory components """
        data = 'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00' \
                   '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        storage=SimpleUploadedFile("foo.png", data)
        f = self.type.model(storage=storage, filename="/etc/passwd").save()
        assert f.filename == "passwd"

        f = self.type.model(storage=storage, filename="../foo.png").save()
        assert f.filename == "foo.png"

    def test_download_state(self, client):
        """ file must be "visible" in order to be downloadable """
        pytest.skip("TODO XXX")

class TestImageSpokeTemplate(BaseImageFileTemplateTest):
    """
        Test the image spoke
    """
    type = ImageType
    typename = "image"


class TestImageSpoke(BaseImageFileTest):
    """
        Test the image spoke
    """
    type = ImageType
    typename = "image"

class TestImageSpokeImpExp(BaseSpokeImportExportTest):
    type = Image
    spoke = ImageType

class TestFileSpokeTemplate(BaseImageFileTemplateTest):
    """
        Test the file spoke
    """
    type = FileType
    typename = "file"


class TestFileSpoke(BaseImageFileTest):
    """
        Test the file spoke

    """
    type = FileType
    typename = "file"

class TestImageFileImpExp(BaseSpokeImportExportTest):
    type = File
    spoke = FileType
