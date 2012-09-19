import urllib
import urlparse
import re

from google.appengine.api import datastore_errors
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