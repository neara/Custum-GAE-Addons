import unittest
from google.appengine.api import datastore_errors

from google.appengine.ext import testbed, ndb
from cndb.properties import URLProperty, ImgProperty

class TestURLProperty(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_creation(self):
        class Model(ndb.Model):
            url = URLProperty()

        k = Model(
            url = 'http://blah.com/'
        ).put()

        self.assertTrue(k is not None)

    def test_required(self):
        class Model(ndb.Model):
            url = URLProperty(required=True)

        with self.assertRaises(datastore_errors.BadValueError):
            Model().put()

    def test_validation(self):
        class Model(ndb.Model):
            url = URLProperty()

        with self.assertRaises(datastore_errors.BadValueError):
            Model(url='google.com')

        with self.assertRaises(datastore_errors.BadValueError):
            Model(url='blahblah')

        o2 = Model(url='http://google.com/')
        o2.put()

        q = Model.query(Model.url == 'http://google.com/')
        self.assertEqual(q.count(), 1)

    def test_usage(self):
        class Model(ndb.Model):
            url = URLProperty()

        k = Model(url='http://google.com/').put()
        import requests
        req = requests.get(k.get().url)
        self.assertTrue(req.status_code == requests.codes.ok)


class TestImgProperty(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_images_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_creation(self):
        class Model(ndb.Model):
            img = ImgProperty()

        m = Model(img='http://www.weareblahblahblah.com/wp-content/themes/blahblahblah/images/bbb-facebook-button.jpg')
        k = m.put()
        self.assertTrue(k.get() is not None)

if __name__ == 'main':
    unittest.main()