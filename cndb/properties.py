import imghdr
import urllib
import urlparse
import re

from google.appengine.api import datastore_errors, images
from google.appengine.api.images import Image
from google.appengine.ext import ndb


class URLProperty(ndb.StringProperty):

    parts = ()

    def _validate(self, value):
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not regex.search(value):
            raise datastore_errors.BadValueError('Not valid URL')

        scheme, netloc, path, query, fragment = urlparse.urlsplit(value)
        if not scheme:
            raise datastore_errors.BadValueError('Not valid URL. Please specify scheme: http, https, ftp.')

        path = urllib.pathname2url(path)
        query = urllib.urlencode(query)

        self.parts = (scheme, netloc, path, query, fragment)

    def _to_base_type(self, value):
        return urlparse.urlunsplit(self.parts)

class ImgProperty(ndb.BlobProperty):

    def __init__(self, width=0, height=0, **kwds):
        self._width = width
        self._height = height
        self._img_data = ''
        super(ImgProperty, self).__init__(**kwds)

    def _validate(self, value):
        """
        Validating the format of received image file
        """
        fp = urllib.urlopen(value)
        self._img_data = fp.read()

        if imghdr.what(fp, self._img_data) not in ['jpeg', 'png', 'webp', 'bmp', 'gif', 'ico', 'tiff']:
            raise TypeError('Unrecognised format. We accept only: jpeg, png, bmp, gif or tiff')

    def _to_base_type(self, value):
        """
        Transforming the image and saving it to blobstore
        """
        img = Image(self._img_data)
        if self._width > 0 or self._height > 0:
            img.resize(width=self._width, height=self._height)
        img.im_feeling_lucky()
        return img.execute_transforms(output_encoding=images.JPEG)

class EmailProperty(ndb.StringProperty):
    def _validate(self, value):
        email_regex = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
            # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
            r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)'  # domain
            r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3))

        if not email_regex.search(value):
            raise datastore_errors.BadValueError('Not a valid email address!')